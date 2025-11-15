# refiner.py
from config import model


def run_refiner(latex_code: str, audit_results: dict) -> str:
    """
    Polish latex_code using audit_results to decide whether to
    inject caption/label placeholders and to act on auditor feedback.
    """
    print("[Refiner Tool]: Refining LaTeX...")

    has_caption = audit_results.get("has_caption", False)
    has_label = audit_results.get("has_label", False)
    issues = audit_results.get("issues", [])
    suggestions = audit_results.get("suggestions", [])
    column_mismatches = audit_results.get("column_mismatch_rows") or []
    needs_tabular_scaffold = audit_results.get("needs_tabular_scaffold", False)
    placeholder_headers = audit_results.get("placeholder_headers") or []
    expected_columns = audit_results.get("expected_columns")

    audit_summary_lines = ["- No structural issues detected."]
    if issues:
        audit_summary_lines = [f"- {item}" for item in issues]
    if column_mismatches:
        audit_summary_lines.append(f"- Column mismatches on rows: {column_mismatches}")

    suggestion_lines = [f"- {text}" for text in suggestions] if suggestions else ["- Follow the core table cleanup rules."]
    audit_summary = "\n".join(audit_summary_lines)
    suggestion_summary = "\n".join(suggestion_lines)
    header_guidance = ", ".join(placeholder_headers) if placeholder_headers else "Use the existing column headings."
    expected_cols_note = expected_columns if expected_columns else "the appropriate number of"

    prompt = f"""
You are an expert LaTeX assistant. Take the following LaTeX table and 
improve it based on these rules:

1.  **Make it compact & professional:** Use the `booktabs` package. 
    Add `\toprule`, `\midrule`, and `\bottomrule`.
2.  **Clean up:** Remove all vertical lines (`|`) and `\hline`.
3.  **Center it:** Ensure `\centering` is present.
4.  **Placement:** Use `[htbp]` for the table environment.
5.  **Caption (Audit = {has_caption}):** If this is False, add a 
    placeholder: `\caption{{Add your caption here}}`
6.  **Label (Audit = {has_label}):** If this is False, add a 
    placeholder *after* the caption: `\label{{Add your label here}}`
7.  **Honor the auditor report below before making other changes.**
8.  **Tabular scaffold needed (Audit = {needs_tabular_scaffold}):** If True, wrap the rows in a full `\begin{{tabular}}...\end{{tabular}}` with {expected_cols_note} columns.
9.  **Header guidance:** If a header is missing, insert this placeholder header row (bold each column): {header_guidance}.
10. **Do not change any of the user's actual data, text, or numbers.**

Audit summary:
{audit_summary}

Suggested fixes from the auditor:
{suggestion_summary}

Respond with *only* the complete, final LaTeX code block.

Here is the table to refine:
{latex_code}
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error in refiner: {e}"
