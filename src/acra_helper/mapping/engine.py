"""
Mapping engine: Excel label  →  (element, context_key)

mapping.yaml structure:
  mappings:
    - label: "Cash and bank balances"
      element: "sg-as:CashAndBankBalances"
      contexts:              # list of context_keys this label applies to
        - asof_20251231
        - asof_20241231
"""
from pathlib import Path
from typing import Any

import yaml


def load_mapping(mapping_path: Path) -> list[dict]:
    data = yaml.safe_load(mapping_path.read_text(encoding="utf-8"))
    return data.get("mappings", [])


def apply_mapping(
    parsed_excel: dict[str, dict[str, Any]],
    mappings: list[dict],
) -> tuple[list[dict], list[str]]:
    """
    Match Excel labels to taxonomy elements.

    Returns:
        mapped:   [{element, context, value}, ...]
        unmapped: [label, ...]  — labels with no match
    """
    mapping_index: dict[str, dict] = {
        m["label"].strip().lower(): m for m in mappings
    }

    mapped: list[dict] = []
    unmapped: list[str] = []

    for label, values in parsed_excel.items():
        key = label.strip().lower()
        rule = mapping_index.get(key)

        if rule is None:
            unmapped.append(label)
            continue

        element = rule["element"]
        for ctx in rule.get("contexts", []):
            # Find the matching value column — context key encodes the year
            year = _year_from_context(ctx)
            value = _pick_value(values, year)
            if value is not None:
                mapped.append({"element": element, "context": ctx, "value": value})

    return mapped, unmapped


def _year_from_context(ctx: str) -> str | None:
    """Extract 4-digit year from context key (last occurrence wins for asof_, first for fromto_)."""
    import re
    years = re.findall(r"\d{4}", ctx)
    if not years:
        return None
    return years[-1]  # e.g. asof_20251231 → "2025", fromto_20240101_20241231 → "2024"


def _pick_value(values: dict[str, Any], year: str | None) -> float | None:
    if year is None:
        return None
    for col, val in values.items():
        if year in str(col) and val is not None:
            return val
    return None
