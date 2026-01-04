"""
Judge Engine Service
--------------------
Orchestrates the AI evaluation process.
Supports:
1. Multi-Persona Consensus (Consensus Panel)
2. Single Persona Evaluation
3. Multimodal Analysis (Video + Text + Code)

Integrates with Google Gemini (Primary) and potentially Anthropic Claude (Secondary/Disabled).

Author: Dwarkesh Ramani & Team
"""

import os
import asyncio
import json
import statistics

# Third-party imports
from google import genai
from google.genai import types
import anthropic

# ==========================================
# Main Entry Point
# ==========================================

async def evaluate_project(repo_data: str, transcript: str, doc_text: str, ppt_text: str = "", persona: str = "standard", video_metadata: dict = None, gemini_file_obj=None):
    """
    Main entry point for project evaluation.
    Routes to single or multi-judge panel based on configured persona.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "Missing GEMINI_API_KEY"}
    
    if video_metadata is None:
        video_metadata = {}
    
    if persona == "consensus":
        return await run_consensus_panel(repo_data, transcript, doc_text, ppt_text, video_metadata, gemini_file_obj)

    # Single Persona Execution
    return await _evaluate_single_persona(api_key, repo_data, transcript, doc_text, ppt_text, persona, video_metadata, gemini_file_obj)

# ==========================================
# Consensus Panel Logic
# ==========================================

async def run_consensus_panel(repo_data, transcript, doc_text, ppt_text, video_metadata, gemini_file_obj=None):
    """
    Runs multiple judge personas in parallel and aggregates their scores.
    """
    judges = ["vc", "cto", "product", "uiux", "professor"]
    
    print(f"INFO: Starting Consensus Panel with judges: {judges}")
    
    # Run all judges in parallel
    tasks = [
        _evaluate_single_persona(os.getenv("GEMINI_API_KEY"), repo_data, transcript, doc_text, ppt_text, role, video_metadata, gemini_file_obj)
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
    
    # Helper to safely parse scores
    def safe_get_score(data, key):
        val = data.get(key, 0)
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            # Remove % if present and try to parse
            clean_val = val.replace('%', '').strip()
            try:
                return float(clean_val)
            except ValueError:
                return 0
        return 0

    for res in valid_results:
        aggregated["innovation_score"] += safe_get_score(res, "innovation_score")
        aggregated["technical_score"] += safe_get_score(res, "technical_score")
        aggregated["relevance_score"] += safe_get_score(res, "relevance_score")
        aggregated["ui_ux_score"] += safe_get_score(res, "ui_ux_score")
        aggregated["impact_score"] += safe_get_score(res, "impact_score")
        aggregated["presentation_score"] += safe_get_score(res, "presentation_score")
        aggregated["win_probability"] += safe_get_score(res, "win_probability")
        
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

# ==========================================
# Single Persona Logic
# ==========================================

async def _evaluate_single_persona(gemini_api_key, repo_data, transcript, doc_text, ppt_text, persona, video_metadata=None, gemini_file_obj=None):
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
    
    if video_metadata is None:
        video_metadata = {}
    
    # Build video context for better analysis
    video_context = ""
    if video_metadata.get("available"):
        video_context = f"""
VIDEO METRICS:
- Word Count: {video_metadata.get('word_count', 0)}
- Estimated Duration: {video_metadata.get('estimated_duration_minutes', 0)} minutes
- Filler Words: {video_metadata.get('filler_word_count', 0)} ({video_metadata.get('filler_percentage', 0)}%)
- Quality Notes: {video_metadata.get('quality_notes', 'N/A')}
"""
    else:
        video_context = f"VIDEO METRICS: Not available - {video_metadata.get('quality_notes', 'No video provided')}"

    prompt = f"""
    ROLE: {role_description}
    
    TASK: Evaluate this hackathon project based on the inputs below.
    
    INPUTS:
    CODE SUMMARY: {repo_data[:5000]}
    VIDEO TRANSCRIPT: {transcript[:5000]}
    {video_context}
    DOCS: {doc_text[:3000]}
    PPT SLIDES: {ppt_text[:3000]}
    
    IMPORTANT: For video_analysis, use the VIDEO METRICS above to inform your scoring:
    - clarity_score: Based on filler word percentage (low % = high score)
    - pacing_score: Based on words per minute and duration (too fast or slow = lower score)
    - confidence_score: Infer from language patterns in transcript
    - filler_words: "low" if <3%, "medium" if 3-5%, "high" if >5%
    - comments: Provide specific feedback on presentation quality
    
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
            "comments": "Analysis of speech and presentation quality based on the metrics"
        }}
    }}
    """
    
    # 1. Try Claude (Anthropic) - DISABLED per user request
    # anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    # if anthropic_key:
    #     try:
    #         print(f"DEBUG: Attempting to use Claude for {persona}...")
    #         return await _evaluate_with_claude(anthropic_key, prompt)
    #     except Exception as e:
    #         print(f"WARNING: Claude API failed: {e}. Falling back to Gemini.")
    # else:
    #     print("DEBUG: No ANTHROPIC_API_KEY found. Using Gemini.")

    # 2. Fallback to Gemini
    return await _evaluate_with_gemini(gemini_api_key, prompt, gemini_file_obj)

async def _evaluate_with_claude(api_key, prompt):
    client = anthropic.AsyncAnthropic(api_key=api_key)
    message = await client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    # Extract JSON from potential text wrapping
    content = message.content[0].text
    # Simple cleanup if Claude adds markdown code blocks
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1]
    return content.strip()

async def _evaluate_with_gemini(api_key, prompt, gemini_file_obj=None):
    if not api_key:
        return json.dumps({"error": "Missing GEMINI_API_KEY for fallback"})
        
    client = genai.Client(api_key=api_key)
    try:
        # Prepare contents (multimodal if file provided)
        contents = [prompt]
        if gemini_file_obj:
            print("INFO: Using multimodal input (video file) for Gemini...")
            contents = [gemini_file_obj, prompt]

        # Fixed Model Name: gemini-2.5-flash
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return response.text
    except Exception as e:
        print(f"ERROR calling Gemini: {str(e)}")
        return json.dumps({"error": f"Both AI models failed. Gemini Error: {str(e)}"})

async def generate_roast(input_text: str):
    """
    Generates a quick, brutal roast for invalid submissions.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "I can't even roast you properly because the API key is missing. Pathetic."
    
    client = genai.Client(api_key=api_key)
    try:
        prompt_text = f"The user provided this garbage: \"{input_text}\"\nRoast them for being incompetent. Be brief (2 sentences) but brutal."
        response = await client.aio.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt_text
        )
        return response.text
    except Exception as e:
        return f"I tried to roast you but even that failed: {e}"
