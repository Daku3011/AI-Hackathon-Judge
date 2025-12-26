from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from services.github_analyzer import analyze_repo
from services.video_analyzer import get_video_transcript
from services.doc_analyzer import extract_text_from_pdf
from services.judge_engine import evaluate_project, generate_roast
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read version from VERSION file
VERSION = "1.1.3"
try:
    with open(os.path.join(os.path.dirname(__file__), "VERSION"), "r") as f:
        VERSION = f.read().strip()
except (FileNotFoundError, IOError):
    pass

app = FastAPI(
    title="AI Project Judge",
    version=VERSION,
    description="An AI-powered tool that analyzes your GitHub repository and demo video to provide instant scores, feedback, and a reality check."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the 'assets' directory from the frontend build
import sys

if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    base_path = os.path.dirname(sys.executable)
    # PyInstaller v6+ puts contents in _internal by default
    internal_path = os.path.join(base_path, "_internal")
    if os.path.exists(internal_path):
        base_path = internal_path
    
    frontend_dist = os.path.join(base_path, "frontend", "dist")
else:
    # Running in a normal Python environment
    base_path = os.path.dirname(os.path.dirname(__file__))
    frontend_dist = os.path.join(base_path, "frontend", "dist")

assets_path = os.path.join(frontend_dist, "assets")

if os.path.isdir(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
else:
    print(f"WARNING: Frontend assets not found at {assets_path}. Run 'npm run build' in frontend directory.")

class ProjectSubmission(BaseModel):
    github_url: str
    video_url: Optional[str] = None
    persona: Optional[str] = "standard"

@app.get("/api")
def read_root():
    return {
        "message": "AI Project Judge API is running",
        "version": VERSION
    }

@app.post("/analyze")
async def analyze_project(submission: ProjectSubmission):
    # 1. Analyze Repo
    repo_data = analyze_repo(submission.github_url)
    
    # Check for invalid repo
    if repo_data.get("files_count", 0) == 0 or "Invalid" in repo_data.get("summary", ""):
        # Generate Roast
        roast_msg = await generate_roast(submission.github_url)
        return {
             "scores": { "innovation": 0, "quality": 0, "uiux": 0, "impact": 0 },
             "feedback": roast_msg,
             "whyWontWin": "Because you didn't even submit a real project."
        }
        
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
                "technical": 7,
                "relevance": 9,
                "uiux": 9,
                "impact": 8,
                "presentation": 7
            },
            "strengths": [
                "Clean project structure",
                "Good use of modern frameworks",
                "Clear documentation"
            ],
            "improvements": [
                "Add more unit tests",
                "Improve error handling",
                "Add a demo video"
            ],
            "questions": [
                "How do you handle scalability?",
                "What was the biggest technical challenge?"
            ],
            "feedback": "Gemini API Key missing. Returning demo feedback.\n\nThe project structure looks good. Consider adding more unit tests.",
            "whyWontWin": "The UI is basic. Adding animations would help."
         }

    analysis_result = await evaluate_project(repo_summary, transcript, doc_text, submission.persona)
    
    # Check if analysis_result is already a dict (error from judge_engine)
    if isinstance(analysis_result, dict):
        return {
            "scores": { "innovation": 0, "technical": 0, "relevance": 0, "uiux": 0, "impact": 0, "presentation": 0 },
            "feedback": f"Error during analysis: {analysis_result.get('error')}",
            "whyWontWin": "N/A"
        }

    # Parse the LLM output (assuming it returns JSON string)
    try:
        data = json.loads(analysis_result)

        # Map LLM flat structure to Frontend nested structure
        return {
            "scores": {
                "innovation": data.get("innovation_score", 0),
                "technical": data.get("technical_score", data.get("code_quality_score", 0)),
                "relevance": data.get("relevance_score", 0),
                "uiux": data.get("ui_ux_score", 0),
                "impact": data.get("impact_score", 0),
                "presentation": data.get("presentation_score", 0)
            },
            "strengths": data.get("key_strengths", []),
            "improvements": data.get("areas_for_improvement", []),
            "questions": data.get("suggested_questions", []),
            "feedback": data.get("summary_feedback", "No feedback provided."),
            "whyWontWin": data.get("why_it_wont_win", "N/A")
        }
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        print(f"Raw Output: {analysis_result}")
        return {
             "scores": { "innovation": 0, "technical": 0, "relevance": 0, "uiux": 0, "impact": 0, "presentation": 0 },
             "feedback": f"Failed to parse AI response. Raw output logged.",
             "whyWontWin": "N/A"
        }

@app.get("/{catchall:path}")
async def serve_frontend(catchall: str):
    # Serve index.html for any other route (SPA)
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found"}

if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    
    # Required for PyInstaller on Windows
    multiprocessing.freeze_support()
    
    print(f"Starting Project Judge v{VERSION}...")
    print(f"Serving frontend from: {frontend_dist}")
    
    # Determine port
    port = int(os.environ.get("PORT", 8000))
    
    # Run server
    # Pass app instance directly for frozen builds
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False, workers=1)
