# main.py
from auditor import audit_latex_table
from router import run_router
from llm_tools import run_formatter
from refiner import run_refiner
from pathlib import Path
import sys # We'll use this to read filenames

def run_agent(input_data: str):
    """
    Runs the full agent logic.
    """
    print("AGENT STARTED")

    if not input_data or not input_data.strip():
        print("[Agent]: No content detected in the input. Skipping tool calls.")
        print("  🤖 AGENT FINISHED  ")
        return "Error: No input data provided."
    
    # Step 1: Run the Router to classify the input
    input_type = run_router(input_data)
    
    # Step 2: Conditional Logic
    if input_type == 'plain':
        # If plain text, run the Formatter first
        current_latex = run_formatter(input_data)
    else:
        # If it's already LaTeX, just pass it through
        current_latex = input_data
        
    # Step 3: Run the Auditor (code-only tool)
    audit_results = audit_latex_table(current_latex)
    issues = audit_results.get("issues") or []
    if issues:
        print("[Agent]: Auditor flagged these items before refinement:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("[Agent]: Auditor did not flag any structural issues.")
    
    # Step 4: Run the Refiner
    final_latex = run_refiner(current_latex, audit_results)
    
    print("AGENT STARTED")
    return final_latex

def read_file(filename: str) -> str:
    """Reads the content of a file and returns it."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        sys.exit(1) # Exit the script with an error
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def save_tex_and_preview(latex_code: str, base_name: str) -> None:
    """
    Persist the model output to outputs/<base_name>.tex so you can open
    it later in a LaTeX editor or include it in a document.
    """
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    tex_path = output_dir / f"{base_name}.tex"
    tex_path.write_text(latex_code, encoding="utf-8")
    print(f"[Output]: LaTeX saved to {tex_path}")

#  EXAMPLE USAGE 
if __name__ == "__main__":
    
    #   Test 1: Run with PLAIN TEXT file  
    print(" TEST 1: Reading from input_plain.txt ")
    plain_text_input = read_file("input_plain.txt")
    final_table_1 = run_agent(plain_text_input)
    
    print("\n   FINAL OUTPUT 1   \n")
    print(final_table_1)
    save_tex_and_preview(final_table_1, "output_plain")
    
    
    #   Test 2: Run with LATEX file  
    print("\n\n  TEST 2: Reading from input_latex.txt  ")
    latex_input = read_file("input_latex.txt")
    final_table_2 = run_agent(latex_input)
    
    print("\n   FINAL OUTPUT 2   \n")
    print(final_table_2)
    save_tex_and_preview(final_table_2, "output_latex")
