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
        "standard": "You are an expert Hackathon Judge. Evaluate comprehensively.",
        "vc": "You are a ruthless Venture Capitalist (VC). You don't care about code cleanliness, you only care about: Is this a business? How do I make 100x return? Is the market big enough? Ignore technical debt, focus on scalability and revenue. Be skeptical.",
        "cto": "You are a grumpy CTO. You care DEEPLY about code quality, architecture, security, and scalability. Does it utilize best practices? Is it modular? Are there tests? If the code is messy, destroy the score. Ignore the 'business potential'.",
        "roast": "You are a Roast Master. You are mean, funny, and brutal. Your goal is to roast the project while judging it. Make fun of the tech stack choices, the inconsistent variable names, the lack of comments, or the generic idea. Be entertaining but technically accurate."
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
