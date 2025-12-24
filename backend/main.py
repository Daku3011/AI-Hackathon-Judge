from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from services.github_analyzer import analyze_repo
from services.video_analyzer import get_video_transcript
from services.doc_analyzer import extract_text_from_pdf
from services.judge_engine import evaluate_project
import json

app = FastAPI(title="AI Project Judge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProjectSubmission(BaseModel):
    github_url: str
    video_url: Optional[str] = None
    persona: Optional[str] = "standard"

@app.get("/")
def read_root():
    return {"message": "AI Project Judge API is running"}

@app.post("/analyze")
async def analyze_project(submission: ProjectSubmission):
    # 1. Analyze Repo
    repo_data = analyze_repo(submission.github_url)
    repo_summary = json.dumps(repo_data) # Convert to string for LLM

    # 2. Analyze Video
    transcript = ""
    if submission.video_url:
        # Extract video ID from URL (basic logic)
        try:
            video_id = submission.video_url.split("v=")[1].split("&")[0]
            transcript = get_video_transcript(video_id)
        except:
             transcript = "Could not extract video ID or transcript."

    # 3. Analyze Docs (Placeholder for file upload logic if added)
    doc_text = "No documents provided."

    # 4. Judge
    # For now, return a mock if no API key, or try to call if key exists
    import os
    if not os.getenv("GEMINI_API_KEY"):
         # Mock response for demo purposes if no key
         return {
            "scores": {
                "innovation": 8,
                "quality": 7,
                "uiux": 9,
                "impact": 8
            },
            "feedback": "Gemini API Key missing. Returning demo feedback.\n\nThe project structure looks good. Consider adding more unit tests.",
            "whyWontWin": "The UI is basic. Adding animations would help."
         }

    analysis_result = evaluate_project(repo_summary, transcript, doc_text, submission.persona)
    
    # Check if analysis_result is already a dict (error from judge_engine)
    if isinstance(analysis_result, dict):
        return {
            "scores": { "innovation": 0, "quality": 0, "uiux": 0, "impact": 0 },
            "feedback": f"Error during analysis: {analysis_result.get('error')}",
            "whyWontWin": "N/A"
        }

    # Parse the LLM output (assuming it returns JSON string)
    import re
    try:
        # Robust JSON extraction: Find content between first { and last }
        match = re.search(r'\{.*\}', analysis_result, re.DOTALL)
        if match:
             json_str = match.group(0)
             try:
                data = json.loads(json_str)
             except json.JSONDecodeError:
                # Fallback: Try analyzing as Python dict (handles single quotes)
                import ast
                try:
                    data = ast.literal_eval(json_str)
                except:
                    raise ValueError("Could not parse JSON or Python Dict")
        else:
             raise ValueError("No JSON object found in response")

        # Map LLM flat structure to Frontend nested structure
        return {
            "scores": {
                "innovation": data.get("innovation_score", 0),
                "quality": data.get("code_quality_score", 0),
                "uiux": data.get("ui_ux_score", 0),
                "impact": data.get("impact_score", 0)
            },
            "feedback": data.get("summary_feedback", "No feedback provided."),
            "whyWontWin": data.get("why_it_wont_win", "N/A")
        }
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        print(f"Raw Output: {analysis_result}")
        return {
             "scores": { "innovation": 0, "quality": 0, "uiux": 0, "impact": 0 },
             "feedback": f"Failed to parse AI response. Raw output logged.",
             "whyWontWin": "N/A"
        }
