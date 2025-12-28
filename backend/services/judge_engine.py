import google.generativeai as genai
import os

async def evaluate_project(repo_data: str, transcript: str, doc_text: str, ppt_text: str = "", persona: str = "standard"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "Missing GEMINI_API_KEY"}
    
    genai.configure(api_key=api_key)
    
    # Fallback to standard gemini-2.5-flash which is most widely supported
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
    except Exception as e:
         print(f"Error creating model: {e}")
         return {"error": f"Model creation failed: {e}"}

    # print(f"DEBUG: calling gemini-pro with key: {api_key[:5]}...")
    print(f"DEBUG: PPT Text Length: {len(ppt_text)}")
    
    
    # Define Persona Prompts
    persona_prompts = {
        "standard": """You are a Fair & Experienced Hackathon Judge. Your goal is to evaluate projects objectively and constructively.
        You evaluate based on the following comprehensive criteria:
        
        1. **Innovation & Originality**: Is the solution unique? Does it approach the problem in a novel way?
        2. **Technical Implementation**: Code quality, complexity, functionality, and use of technology.
        3. **Problem Statement & Relevance**: Does it address a real, clearly defined problem?
        4. **User Experience (UX/UI)**: Intuitiveness, design, and flow.
        5. **Potential Impact/Feasibility**: Scalability, real-world applicability, and market potential.
        6. **Presentation & Teamwork**: Clarity of the demo, explanation of choices, and evidence of collaboration.
        
        You must provide valuable, constructive feedback, highlighting both strengths and weaknesses. You also need to suggest technical questions to ask the team during Q&A.""",
        
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
    
    PPT SLIDES CONTENT:
    {ppt_text[:5000]}
    
    SPECIAL INSTRUCTIONS FOR PPT:
    1. **Project Relevance**: Verify if the PPT content matches the project described in the code and video. If it seems unrelated or generic, be rude/dismissive in the feedback.
    2. **AI Detection (STRICT)**: You must aggressively detect AI-generated content. Look for:
       - Generic buzzwords ("Revolutionizing", "Unlocking potential", "In today's fast-paced world").
       - Perfect, robotic structure with lack of specific implementation details or constraints.
       - Hallucinated features not found in the code.
       - If it feels like a ChatGPT copy-paste, mark "is_ai_generated": true.
       - If it has typos, specific rigid technical diagrams explained poorly, or deeply specific human nuance, mark "is_ai_generated": false. 
    
    Provide a strictly valid JSON output with the following schema:
    {{
        "innovation_score": 5,
        "technical_score": 5,
        "relevance_score": 5,
        "ui_ux_score": 5,
        "impact_score": 5,
        "presentation_score": 5,
        "key_strengths": ["string", "string"],
        "areas_for_improvement": ["string", "string"],
        "suggested_questions": ["string", "string"],
        "summary_feedback": "string",
        "why_it_wont_win": "string",
        "ppt_analysis": {{
            "is_relevant": true,
            "is_ai_generated": true,
            "comments": "string"
        }}
    }}
    Ensure all keys are double-quoted.
    """
    
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        print(f"DEBUG: Gemini response received: {response.text[:100]}...")
        return response.text
    except Exception as e:
        print(f"ERROR calling Gemini: {str(e)}")
        return {"error": str(e)}

async def generate_roast(input_text: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "I can't even roast you properly because the API key is missing. Pathetic."
    
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"""
        The user was supposed to provide a valid GitHub URL or project details.
        Instead, they provided this garbage: "{input_text}"
        
        You are a sarcastic, mean, and funny AI judge. 
        Roast the user for being incompetent / trying to trick the system / inputting random nonsense.
        Be brief (max 2 sentences) but brutal. Make it sound like you are disappointed in their existence.
        """
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        return f"I tried to roast you but even that failed: {e}"
