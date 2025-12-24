import google.generativeai as genai
import os

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No GEMINI_API_KEY found in environment.")
else:
    genai.configure(api_key=api_key)
    print(f"Checking models for key: {api_key[:5]}...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Found model: {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
