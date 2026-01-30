
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Force reload to pick up the changes
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GEMINI_MODEL")

print(f"Testing model: {model_name}")

if not api_key:
    print("API Key not found!")
else:
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, can you hear me?")
        print("Response received successfully:")
        print(response.text)
    except Exception as e:
        print(f"Error during generation: {e}")
