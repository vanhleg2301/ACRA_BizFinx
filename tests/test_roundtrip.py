"""
Round-trip test: load seed facts + calc rules → validation must pass with 0 mismatches.
This is the safety net that must stay green before any further development.
"""
import json
from pathlib import Path
from datetime import date

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def calc_rules() -> dict:
    return json.loads((FIXTURES / "calc_rules_seed.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fact_map() -> dict:
    return json.loads((FIXTURES / "fact_map_seed.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def seed_contexts() -> dict:
    return json.loads((FIXTURES / "contexts.json").read_text(encoding="utf-8"))


# ── Task 3: contexts builder ──────────────────────────────────────────────────

class TestContextsBuilder:
    def test_generates_17_contexts(self, seed_contexts):
        from acra_helper.taxonomy.contexts import build_contexts

        built = build_contexts(date(2025, 12, 31))
        assert len(built) == 17

    def test_keys_match_seed(self, seed_contexts):
        from acra_helper.taxonomy.contexts import build_contexts

        built = build_contexts(date(2025, 12, 31))
        assert set(built.keys()) == set(seed_contexts.keys())

    def test_period_values_match_seed(self, seed_contexts):
        from acra_helper.taxonomy.contexts import build_contexts

        built = build_contexts(date(2025, 12, 31))
        for key, expected in seed_contexts.items():
            assert built[key]["period"] == expected["period"], f"period mismatch for {key}"

    def test_dimension_values_match_seed(self, seed_contexts):
        from acra_helper.taxonomy.contexts import build_contexts

        built = build_contexts(date(2025, 12, 31))
        for key, expected in seed_contexts.items():
            assert built[key]["dimension"] == expected["dimension"], (
                f"dimension mismatch for {key}"
            )


# ── Task 4: calc validator round-trip ────────────────────────────────────────

class TestCalcRoundtrip:
    def test_no_mismatches_on_seed(self, fact_map, calc_rules):
        from acra_helper.validate.calc_validator import build_numeric_fact_index, validate

        index = build_numeric_fact_index(fact_map["facts"])
        mismatches = validate(index, calc_rules)

        if mismatches:
            lines = [
                f"  {m['rule']} @ {m['context']}: "
                f"computed={m['computed']:.2f} reported={m['reported']:.2f} diff={m['diff']:.2f}"
                for m in mismatches
            ]
            pytest.fail("Calc mismatches found:\n" + "\n".join(lines))

    def test_fact_index_numeric_only(self, fact_map):
        from acra_helper.validate.calc_validator import build_numeric_fact_index

        index = build_numeric_fact_index(fact_map["facts"])
        # All values must be float
        for element, ctx_map in index.items():
            for ctx, val in ctx_map.items():
                assert isinstance(val, float), f"{element}@{ctx} is not float"

    def test_known_parents_are_present(self, fact_map):
        from acra_helper.validate.calc_validator import build_numeric_fact_index

        index = build_numeric_fact_index(fact_map["facts"])
        for parent in ["Assets", "CurrentAssets", "NoncurrentAssets", "Liabilities",
                       "Equity", "Revenue", "ProfitLossBeforeTaxation"]:
            assert parent in index, f"Expected parent '{parent}' in fact index"

    @pytest.mark.parametrize("parent,ctx,expected", [
        ("Assets",              "asof_20251231",              3645871),
        ("Assets",              "asof_20241231",              3629875),
        ("CurrentAssets",       "asof_20251231",               779871),
        ("NoncurrentAssets",    "asof_20251231",              2866000),
        ("Liabilities",         "asof_20251231",              7106156),
        ("CurrentLiabilities",  "asof_20251231",               -21631),
        ("NoncurrentLiabilities","asof_20251231",             7127787),
        ("Equity",              "asof_20251231",             -3460285),
        ("Revenue",             "fromto_20250101_20251231",     20000),
        ("OtherIncome",         "fromto_20250101_20251231",      2000),
        ("ProfitLossBeforeTaxation", "fromto_20250101_20251231", -83058),
        ("TradeAndOtherReceivables", "asof_20251231",           770415),
        ("TradeAndOtherPayables",    "asof_20251231",           -22491),
        ("LoansAndBorrowings",       "asof_20251231",          6980053),
        ("PropertyPlantAndEquipment","asof_20251231",                0),
    ])
    def test_specific_rule(self, calc_rules, fact_map, parent, ctx, expected):
        from acra_helper.validate.calc_validator import build_numeric_fact_index, validate

        index = build_numeric_fact_index(fact_map["facts"])
        # Filter to just this parent's rules (may appear under multiple rule keys)
        relevant_rules = {
            k: v for k, v in calc_rules.items()
            if k == parent or k.endswith(f"_{parent}")
        }
        mismatches = validate(index, relevant_rules)
        ctx_mismatches = [m for m in mismatches if m["context"] == ctx]
        assert not ctx_mismatches, (
            f"{parent}@{ctx}: {ctx_mismatches}"
        )
        # Also verify the reported value itself
        assert index[parent][ctx] == expected
