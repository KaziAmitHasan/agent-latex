# auditor.py
"""
Utility functions for inspecting LaTeX tables before the refiner runs.
The auditor now surfaces actionable issues so downstream tools (or you)
know exactly what will be fixed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional


TABULAR_BEGIN_RE = re.compile(r"\\begin{tabular}(?:\[[^\]]*\])?{([^}]*)}", re.S)
TABULAR_TOKEN_RE = re.compile(r"\\(begin|end){tabular}")


@dataclass
class TabularBlock:
    column_spec: str
    body: str


def _extract_outer_tabular(latex_code: str) -> Optional[TabularBlock]:
    """
    Grab the first (outermost) tabular environment. We allow nested tabulars
    (for multi-line headers) by scanning until the matching \\end{tabular}.
    """
    begin_match = TABULAR_BEGIN_RE.search(latex_code)
    if not begin_match:
        return None

    depth = 0
    end_idx: Optional[int] = None
    for token in TABULAR_TOKEN_RE.finditer(latex_code, begin_match.start()):
        if token.group(1) == "begin":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end_idx = token.start()
                break

    if end_idx is None:
        return None

    body = latex_code[begin_match.end():end_idx]
    return TabularBlock(column_spec=begin_match.group(1), body=body)


def _count_columns_from_spec(column_spec: str) -> Optional[int]:
    """
    Count how many visible columns a spec defines. We strip helpers like | or @{...}
    and then count alignment tokens (l, c, r, p, m, b, X, S).
    """
    # Remove spacing tweaks such as @{..}
    cleaned = re.sub(r"@{[^}]*}", "", column_spec)
    cleaned = cleaned.replace("|", "")
    tokens = re.findall(r"[lcrpmbXS]", cleaned, re.IGNORECASE)
    return len(tokens) or None


def _find_column_mismatches(tabular_block: TabularBlock, expected_cols: int) -> List[int]:
    """
    Compare each row's column count with the expected value.
    We skip rule commands and nested tabular blocks for sanity.
    """
    mismatched_rows: List[int] = []
    rows = [row.strip() for row in tabular_block.body.split(r"\\") if row.strip()]
    data_row_index = 0

    for row in rows:
        if row.startswith("\\") or "toprule" in row or "midrule" in row or "bottomrule" in row:
            continue
        if "\\begin{tabular" in row or "\\end{tabular" in row:
            continue

        data_row_index += 1
        sanitized = row.replace(r"\&", "")
        col_count = sanitized.count("&") + 1
        if col_count != expected_cols:
            mismatched_rows.append(data_row_index)

    return mismatched_rows


def _count_columns_in_line(line: Optional[str]) -> Optional[int]:
    if not line:
        return None
    sanitized = line.replace(r"\&", "")
    if "&" not in sanitized:
        return None
    return sanitized.count("&") + 1


def audit_latex_table(latex_code: str) -> dict:
    """
    Inspect LaTeX code and return structured feedback + suggestions.
    """
    has_caption = r"\caption" in latex_code
    has_label = r"\label" in latex_code
    has_centering = r"\centering" in latex_code
    uses_toprule = r"\toprule" in latex_code
    uses_midrule = r"\midrule" in latex_code
    uses_bottomrule = r"\bottomrule" in latex_code
    has_bold_header = r"\textbf" in latex_code

    issues: List[str] = []
    suggestions: List[str] = []
    placeholder_headers: List[str] = []
    needs_tabular_scaffold = False

    if not has_caption:
        issues.append("Caption missing.")
        suggestions.append("Add a descriptive caption so readers understand the table.")

    if not has_label:
        issues.append("Label missing.")
        suggestions.append("Add a label for cross-referencing.")

    if not has_centering:
        issues.append("Table is not centered.")
        suggestions.append("Include \\centering inside the table environment.")

    if not (uses_toprule and uses_midrule and uses_bottomrule):
        issues.append("Booktabs rules are incomplete.")
        suggestions.append("Use \\toprule, \\midrule, and \\bottomrule for consistent styling.")

    tabular_block = _extract_outer_tabular(latex_code)
    column_mismatch_rows: List[int] = []
    expected_cols: Optional[int] = None

    if tabular_block:
        expected_cols = _count_columns_from_spec(tabular_block.column_spec)
        if expected_cols:
            column_mismatch_rows = _find_column_mismatches(tabular_block, expected_cols)
            if column_mismatch_rows:
                issues.append(f"Column count mismatch on data rows: {column_mismatch_rows}.")
                suggestions.append("Ensure each row has the same number of cells as the column spec.")
    else:
        needs_tabular_scaffold = True
        issues.append("Tabular environment missing.")
        suggestions.append("Wrap the rows in \\begin{tabular}{...} ... \\end{tabular} with a proper column spec.")

    inferred_cols = None
    if expected_cols:
        inferred_cols = expected_cols
    else:
        first_line_with_amp = next((line for line in latex_code.splitlines() if "&" in line and not line.strip().startswith("%")), None)
        inferred_cols = _count_columns_in_line(first_line_with_amp)
        if inferred_cols is not None:
            expected_cols = inferred_cols

    if not has_bold_header:
        issues.append("Header row missing or not emphasized.")
        suggestions.append("Add a bold header row so each column has a descriptive name.")
        col_count_for_headers = expected_cols or inferred_cols or 3
        placeholder_headers = [f"Column {i+1}" for i in range(max(1, col_count_for_headers))]

    print(f"[Auditor Tool]: Results -> caption={has_caption}, label={has_label}, "
          f"centering={has_centering}, booktabs={uses_toprule and uses_midrule and uses_bottomrule}")

    if issues:
        print("[Auditor Tool]: Issues detected:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("[Auditor Tool]: No structural issues detected.")

    return {
        "has_caption": has_caption,
        "has_label": has_label,
        "has_centering": has_centering,
        "uses_full_booktabs": uses_toprule and uses_midrule and uses_bottomrule,
        "column_mismatch_rows": column_mismatch_rows,
        "expected_columns": expected_cols,
        "needs_tabular_scaffold": needs_tabular_scaffold,
        "placeholder_headers": placeholder_headers,
        "issues": issues,
        "suggestions": suggestions,
    }
