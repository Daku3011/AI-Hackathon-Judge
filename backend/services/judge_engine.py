import google.generativeai as genai
import os

def evaluate_project(repo_data: str, transcript: str, doc_text: str, persona: str = "standard"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "Missing GEMINI_API_KEY"}
    
    # genai.configure(api_key=api_key)
    genai.configure(api_key=api_key)
    
    # Fallback to standard gemini-pro which is most widely supported
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
    except Exception as e:
         print(f"Error creating model: {e}")
         return {"error": f"Model creation failed: {e}"}

    # print(f"DEBUG: calling gemini-pro with key: {api_key[:5]}...")
    
    # DEBUG: List available models to console to help user debug
    # try:
    #     print("DEBUG: Listing available models for this key...")
    #     for m in genai.list_models():
    #         if 'generateContent' in m.supported_generation_methods:
    #             print(f" - {m.name}")
    # except Exception as e:
    #     print(f"DEBUG: Could not list models: {e}")

    
    
    # Define Persona Prompts
    persona_prompts = {
        "standard": "You are a Fair & Experienced Hackathon Judge. You value innovation, execution, and presentation equally. You provide constructive feedback that balances praise with actionable advice.",
        
        "vc": """You are a Silicon Valley VC (Venture Capitalist). You DO NOT CARE about code styles, unit tests, or clean architecture. 
        You ONLY care about:
        1. **Market Size (TAM)**: Is this a billion-dollar opportunity?
        2. **Moat**: Can Google build this in a weekend?
        3. **Viral Loop**: How does it grow?
        4. **Monetization**: How do we make money?
        
        If the project is a "to-do list" or "weather app", destroy it. If it uses AI in a novel way to print money, praise it. 
        Use phrases like "What's the alpha?", "Network effects?", "Scalability?". Be concise and demanding.""",
        
        "cto": """You are a Grumpy Senior Principal Engineer / CTO. You DO NOT CARE about the 'business idea' or 'pretty UI'.
        You ONLY care about:
        1. **Engineering Rigor**: Are there Unit Tests? CI/CD?
        2. **Architecture**: Is it modular or a spaghetti mess?
        3. **Security**: Are they committing API keys? (Check the file list).
        4. **Tech Stack**: Are they using bleeding-edge tools for no reason?
        
        If you see `node_modules` in the repo structure, scream. If there are no comments, deduct points. Hate on 'spaghetti code'. Use technical jargon.""",
        
        "roast": """You are `Gordon Ramsay` meets `StackOverflow Toxic Mod`. Your goal is to be HILARIOUSLY MEAN.
        1. **Roast the Idea**: "Another wrapper around ChatGPT? Original."
        2. **Roast the Code**: "This code looks like it was written by a drunk copilot."
        3. **Roast the Stack**: "jQuery in 2025? Are you a time traveler?"
        
        Do NOT hold back. Be brutal. Be specific. Quote their file names if they are bad. Make the user cry (with laughter)."""
    }
    
    role_description = persona_prompts.get(persona, persona_prompts["standard"])

    prompt = f"""
    {role_description}
    
    Evaluate the following project based on these inputs:
    
    CODE ANALYSIS:
    {repo_data[:5000]}
    
    VIDEO TRANSCRIPT:
    {transcript[:5000]}
    
    DOCUMENTATION:
    {doc_text[:5000]}
    
    Provide a strictly valid JSON output (no markdown, no code blocks, no trailing text):
    {{
        "innovation_score": 5,
        "code_quality_score": 5,
        "ui_ux_score": 5,
        "impact_score": 5,
        "summary_feedback": "string",
        "why_it_wont_win": "string"
    }}
    Ensure all keys are double-quoted. Do not use single quotes for keys or string values.
    """
    
    try:
        response = model.generate_content(prompt)
        print(f"DEBUG: Gemini response received: {response.text[:100]}...")
        return response.text
    except Exception as e:
        print(f"ERROR calling Gemini: {str(e)}")
        return {"error": str(e)}
