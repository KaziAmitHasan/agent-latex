# config.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load all the environment variables from .env
load_dotenv()

# Get the API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("Error: GEMINI_API_KEY environment variable not set.")

# Configure the genai client
genai.configure(api_key=api_key)

# Set up the model with a low temperature for predictable results
generation_config = genai.GenerationConfig(
    temperature=0.0
)

# Create the model instance that our other files will use
# Use the model name you have a key for
model = genai.GenerativeModel(
    model_name="gemini-2.5-pro", 
    generation_config=generation_config
)