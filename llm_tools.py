# llm_tools.py
from config import model 

# --- Tool: The Formatter ---
def run_formatter(plain_text: str) -> str:
    """
    Converts plain text data into a basic LaTeX table.
    """
    print("[Formatter Tool]: Converting plain text to LaTeX...")
    
    # The prompt is an f-string ONLY to insert {plain_text} at the end.
    # The word "table" here is just plain text, not a variable.
    prompt = f"""
You are a data formatter. Convert the following plain text data into a 
basic, unstyled LaTeX table. Use `\begin{{table}}`, `\begin{{tabular}}`, 
and guess the column alignment. Do not add `\caption` or `\label` yet.

Respond with *only* the LaTeX code.

Here is the data:
{plain_text}
"""
    try:
        response = model.generate_content(prompt)
        # We also add .strip() to remove any leading/trailing whitespace
        return response.text.strip()
    except Exception as e:
        return f"Error in formatter: {e}"
