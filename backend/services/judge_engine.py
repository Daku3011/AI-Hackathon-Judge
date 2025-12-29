import google.generativeai as genai
import os
import asyncio
import json
import statistics

async def evaluate_project(repo_data: str, transcript: str, doc_text: str, ppt_text: str = "", persona: str = "standard"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "Missing GEMINI_API_KEY"}
    
    genai.configure(api_key=api_key)
    
    if persona == "consensus":
        return await run_consensus_panel(repo_data, transcript, doc_text, ppt_text)

    # Single Persona Execution
    return await _evaluate_single_persona(api_key, repo_data, transcript, doc_text, ppt_text, persona)

async def run_consensus_panel(repo_data, transcript, doc_text, ppt_text):
    """
    Runs multiple judge personas in parallel and aggregates their scores.
    """
    judges = ["vc", "cto", "product", "uiux", "professor"]
    
    print(f"DEBUG: Starting Consensus Panel with judges: {judges}")
    
    # Run all judges in parallel
    tasks = [
        _evaluate_single_persona(os.getenv("GEMINI_API_KEY"), repo_data, transcript, doc_text, ppt_text, role)
        for role in judges
    ]
    
    results_json_strings = await asyncio.gather(*tasks)
    
    # Aggregate Results
    valid_results = []
    for res_str in results_json_strings:
        try:
            if isinstance(res_str, dict) and "error" in res_str:
                continue
            data = json.loads(res_str)
            valid_results.append(data)
        except:
            continue
            
    if not valid_results:
        return json.dumps({
            "error": "Consensus failed. ALL judges crashed.",
            "innovation_score": 0, "technical_score": 0, "relevance_score": 0, "ui_ux_score": 0, "impact_score": 0, "presentation_score": 0
        })

    # Compute Averages
    aggregated = {
        "innovation_score": 0, "technical_score": 0, "relevance_score": 0, 
        "ui_ux_score": 0, "impact_score": 0, "presentation_score": 0,
        "key_strengths": [], "areas_for_improvement": [], "suggested_questions": [],
        "summary_feedback": "", "why_it_wont_win": "",
        "win_probability": 0
    }
    
    count = len(valid_results)
    
    # Collect all feedback portions
    feedbacks = []
    reasons_loss = []
    
    for res in valid_results:
        aggregated["innovation_score"] += res.get("innovation_score", 0)
        aggregated["technical_score"] += res.get("technical_score", 0)
        aggregated["relevance_score"] += res.get("relevance_score", 0)
        aggregated["ui_ux_score"] += res.get("ui_ux_score", 0)
        aggregated["impact_score"] += res.get("impact_score", 0)
        aggregated["presentation_score"] += res.get("presentation_score", 0)
        aggregated["win_probability"] += res.get("win_probability", 0)
        
        aggregated["key_strengths"].extend(res.get("key_strengths", []))
        aggregated["areas_for_improvement"].extend(res.get("areas_for_improvement", []))
        aggregated["suggested_questions"].extend(res.get("suggested_questions", []))
        
        feedbacks.append(f"[{res.get('judge_name', 'Judge')}] {res.get('summary_feedback', '')}")
        reasons_loss.append(res.get("why_it_wont_win", ""))

    # Finalize Averages
    for key in ["innovation_score", "technical_score", "relevance_score", "ui_ux_score", "impact_score", "presentation_score", "win_probability"]:
        aggregated[key] = round(aggregated[key] / count, 1)

    # Pick top 5 unique strengths/weaknesses to avoid clutter
    aggregated["key_strengths"] = list(set(aggregated["key_strengths"]))[:5]
    aggregated["areas_for_improvement"] = list(set(aggregated["areas_for_improvement"]))[:5]
    aggregated["suggested_questions"] = list(set(aggregated["suggested_questions"]))[:5]
    
    # Merge Feedbacks
    aggregated["summary_feedback"] = "\n\n".join(feedbacks)
    aggregated["why_it_wont_win"] = " | ".join(list(set(reasons_loss))[:3])
    
    # Store Consensus Analysis for simple compatibility
    aggregated["ppt_analysis"] = valid_results[0].get("ppt_analysis", {}) 
    aggregated["video_analysis"] = valid_results[0].get("video_analysis", {})
    aggregated["project_roadmap"] = valid_results[0].get("project_roadmap", [])
    
    return json.dumps(aggregated)


async def _evaluate_single_persona(api_key, repo_data, transcript, doc_text, ppt_text, persona):
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
    except Exception as e:
         return json.dumps({"error": f"Model creation failed: {e}"})

    # Define Persona Prompts
    persona_prompts = {
        "standard": "You are a Fair & Experienced Hackathon Judge. Evaluate objectively.",
        "vc": "You are a Silicon Valley VC. Focus on Market Size, Moat, Viral Loop, and Monetization. Ignore code style. Be demanding.",
        "cto": "You are a Grumpy CTO. Focus on Engineering Rigor, Architecture, Security, and Tech Stack. Hate spaghetti code.",
        "product": "You are a Product Manager. Focus on User Personas, Problem-Solution fit, and UX flows. Ignore technical details.",
        "uiux": "You are a Lead Designer. Focus strictly on Visual Hierarchy, Aesthetics, Accessibility, and User Experience.",
        "professor": "You are a CS Professor. Focus on Algorithms, efficient Time/Space complexity, and theoretical correctness.",
        "roast": "You are a Toxic Internet Troll/Gordon Ramsay. Roast everything. Be mean.",
    }
    
    role_description = persona_prompts.get(persona, persona_prompts["standard"])
    judge_name = persona.upper() if persona != "standard" else "Judge"

    prompt = f"""
    ROLE: {role_description}
    
    TASK: Evaluate this hackathon project based on the inputs below.
    
    INPUTS:
    CODE SUMMARY: {repo_data[:5000]}
    VIDEO TRANSCRIPT: {transcript[:5000]}
    DOCS: {doc_text[:3000]}
    PPT SLIDES: {ppt_text[:3000]}
    
    OUTPUT SCHEMA (JSON ONLY):
    {{
        "judge_name": "{judge_name}",
        "innovation_score": <1-10>,
        "technical_score": <1-10>,
        "relevance_score": <1-10>,
        "ui_ux_score": <1-10>,
        "impact_score": <1-10>,
        "presentation_score": <1-10>,
        "win_probability": <0-100 percentage prediction>,
        "key_strengths": ["string", "string"],
        "areas_for_improvement": ["string", "string"],
        "suggested_questions": ["Technical Question?", "Business Question?", "Viva Question?"],
        "project_roadmap": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
        "summary_feedback": "Your specific feedback in your persona's voice.",
        "why_it_wont_win": "One brutal reason why this loses.",
        "ppt_analysis": {{
            "is_relevant": true,
            "is_ai_generated": false,
            "comments": "Analysis of the slides"
        }},
        "video_analysis": {{
            "clarity_score": <1-10>,
            "pacing_score": <1-10>,
            "confidence_score": <1-10>,
            "filler_words": "low/medium/high",
            "comments": "Analysis of speech and presentation quality"
        }}
    }}
    """
    
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return response.text
    except Exception as e:
        print(f"ERROR calling Gemini for {persona}: {str(e)}")
        return json.dumps({"error": str(e)})

async def generate_roast(input_text: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "I can't even roast you properly because the API key is missing. Pathetic."
    
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"""
        The user provided this garbage: "{input_text}"
        Roast them for being incompetent. Be brief (2 sentences) but brutal.
        """
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        return f"I tried to roast you but even that failed: {e}"
