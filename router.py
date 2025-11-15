# router.py
from config import model


def run_router(input_text: str) -> str:
    """
    Analyze input_text and return 'plain' or 'latex'.
    Keeping the router separate lets you iterate on
    classification logic without touching other tools.
    """
    print("[Router Tool]: Analyzing input type...")

    # Combine instructions and user data in one prompt so
    # the model has all the context it needs.
    prompt = f"""
You are a text classifier. Look at the user's input. Is it a) plain text data, 
or b) LaTeX code? Respond with *only* the single word 'plain' or 'latex'.

Here is the input:
{input_text}
"""
    try:
        response = model.generate_content(prompt)
        decision = response.text.strip().lower()
        print(f"[Router Tool]: Decision is '{decision}'")

        # Fall back to 'plain' if we see an unexpected answer.
        if decision not in ['plain', 'latex']:
            print(f"[Router Tool]: Non-standard response '{decision}', defaulting to 'plain'.")
            return 'plain'
        return decision
    except Exception as e:
        print(f"Error in router: {e}")
        return "plain"
