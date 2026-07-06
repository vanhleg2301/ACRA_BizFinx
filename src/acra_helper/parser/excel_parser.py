"""
Parse a trial balance / financial data Excel file.

Expected layout (flexible):
- Column A (or first col): row label / account name
- Remaining columns: numeric values, with year headers in row 1

Returns: {label: {col_header: value, ...}, ...}
Missing / non-numeric cells are stored as None.
"""
from pathlib import Path
from typing import Any

import openpyxl


def parse_excel(path: Path, sheet_name: str | None = None) -> dict[str, dict[str, Any]]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return {}

    headers = [str(h).strip() if h is not None else f"col_{i}" for i, h in enumerate(rows[0])]
    value_headers = headers[1:]  # skip label column

    result: dict[str, dict[str, Any]] = {}
    for row in rows[1:]:
        if not row or row[0] is None:
            continue
        label = str(row[0]).strip()
        if not label:
            continue
        values: dict[str, Any] = {}
        for header, cell in zip(value_headers, row[1:]):
            if isinstance(cell, (int, float)):
                values[header] = float(cell)
            else:
                values[header] = None
        result[label] = values

    return result
