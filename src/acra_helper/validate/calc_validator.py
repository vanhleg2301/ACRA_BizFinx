"""
Validate XBRL calculation rules against a fact map.

XBRL calc linkbases sometimes include both derivation arcs AND attribution arcs
under the same parent element (different Extended Link Roles in real taxonomy).
When combined into one dict, these produce structural double-counts that are not
true errors. KNOWN_ELR_SPLIT lists such parents to skip strict validation.
"""

KNOWN_ELR_SPLIT: frozenset[str] = frozenset({"ProfitLoss"})


def _local_name(element: str) -> str:
    """Strip namespace prefix: 'sg-as:Foo' or 'sg-as_Foo' -> 'Foo'."""
    if ":" in element:
        return element.split(":", 1)[1]
    if element.startswith("sg-") and "_" in element:
        return element.split("_", 1)[1]
    return element


def build_numeric_fact_index(
    facts: list[dict],
) -> dict[str, dict[str, float]]:
    """
    Convert a flat list of fact dicts into {local_name -> {context_key -> float}}.
    Non-numeric values (strings like 'Yes', dates) are skipped.
    """
    index: dict[str, dict[str, float]] = {}
    for fact in facts:
        raw = fact.get("value", "")
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        local = _local_name(fact["element"])
        ctx = fact["context"]
        index.setdefault(local, {})[ctx] = value
    return index


# Elements that are legitimately bidirectional (a loss, accumulated deficit,
# net gain/loss, or reversal is expected to carry a real sign) — excluded
# from the positive-magnitude convention even though they appear as calc
# rule children.
SIGNED_ELEMENTS: frozenset[str] = frozenset({
    "AccumulatedProfitsLosses",
    "ProfitLossAttributableToOwnersOfCompany",
    "ProfitLossAttributableToNoncontrollingInterests",
    "ProfitLossFromDiscontinuedOperations",
    "OtherGainsLosses",
    "NetGainsLossesOnForeignExchangeAdjustment",
    "NetGainsLossesOnDisposalOfPropertyPlantAndEquipment",
    "NetGainsLossesOnDisposalOfIntangibleAssets",
    "ImpairmentLossReversalOfImpairmentLossOnInvestments",
    "ImpairmentLossReversalOfImpairmentLossOnReceivables",
    "ImpairmentLossReversalOfImpairmentLossOnOthers",
})


def _leaf_children(calc_rules: dict[str, list[dict]]) -> set[str]:
    """Element local names expected to be entered as positive magnitudes.

    ACRA's own BizFinX validator expects detail line items to be positive —
    the +1/-1 weight (not the sign of the value) encodes whether a line adds
    to or subtracts from its parent total. Intermediate rollups (anything
    that is itself a rule parent, e.g. CurrentLiabilities, ProfitLoss) are
    excluded since they legitimately inherit whatever sign their components
    sum to (e.g. a loss-making year), as are known bidirectional elements.
    """
    parents = {_local_name(k) for k in calc_rules}
    children = {
        _local_name(c["child"])
        for rule_children in calc_rules.values()
        for c in rule_children
    }
    return (children - parents) - SIGNED_ELEMENTS


def check_signs(
    facts: list[dict],
    calc_rules: dict[str, list[dict]],
) -> list[dict]:
    """
    Flag mapped facts with a negative value where the element is expected
    to be entered as positive (per calc_rules leaf convention).

    This does NOT auto-correct the value — a negative figure may be a
    legitimate reversal, and blindly flipping it can desync it from a
    parent subtotal that was mapped straight from the same source Excel.
    Returns warnings for manual review before filing.
    """
    expected_positive = _leaf_children(calc_rules)
    warnings: list[dict] = []
    for fact in facts:
        local = _local_name(fact["element"])
        if local not in expected_positive:
            continue
        try:
            value = float(fact["value"])
        except (TypeError, ValueError):
            continue
        if value < 0:
            warnings.append(
                {"element": fact["element"], "context": fact["context"], "value": value}
            )
    return warnings


def validate(
    fact_index: dict[str, dict[str, float]],
    calc_rules: dict[str, list[dict]],
    tolerance: float = 0.5,
) -> list[dict]:
    """
    For each rule in calc_rules, compute sum(child * weight) and compare to
    the reported parent value. Returns a list of mismatch dicts.

    Args:
        fact_index: output of build_numeric_fact_index
        calc_rules: {parent_name: [{child, weight}, ...]}
        tolerance: absolute difference allowed before flagging (handles rounding)
    """
    mismatches: list[dict] = []

    for rule_key, children in calc_rules.items():
        parent_local = _local_name(rule_key)

        if parent_local in KNOWN_ELR_SPLIT:
            continue

        parent_by_ctx = fact_index.get(parent_local, {})
        for ctx, reported in parent_by_ctx.items():
            computed = sum(
                fact_index.get(_local_name(c["child"]), {}).get(ctx, 0.0) * c["weight"]
                for c in children
            )
            diff = computed - reported
            if abs(diff) > tolerance:
                mismatches.append(
                    {
                        "rule": rule_key,
                        "parent": parent_local,
                        "context": ctx,
                        "computed": computed,
                        "reported": reported,
                        "diff": diff,
                    }
                )

    return mismatches
