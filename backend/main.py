from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from services.github_analyzer import analyze_repo
from services.video_analyzer import get_video_transcript, extract_video_id
from services.doc_analyzer import extract_text_from_pdf
from services.judge_engine import evaluate_project, generate_roast
from services.ppt_analyzer import extract_text_from_ppt
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
    internal_path = os.path.join(base_path, "_internal")
    if os.path.exists(internal_path):
        base_path = internal_path
    
    frontend_dist = os.path.join(base_path, "frontend", "dist")
else:
    # Running in a normal Python environment (Local or Docker)
    # Check 1: Multi-stage Docker build location (survives volumes)
    docker_dist = "/frontend_dist"
    # Check 2: Local dev: ../frontend/dist
    local_dist = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist"))
    
    if os.path.isdir(docker_dist):
        frontend_dist = docker_dist
    else:
        frontend_dist = local_dist

assets_path = os.path.join(frontend_dist, "assets")

if os.path.isdir(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
else:
    print(f"WARNING: Frontend assets not found at {assets_path}.")
    print(f"Searched in: {docker_dist} and {local_dist}")

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
async def analyze_project(
    github_url: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    persona: str = Form("standard"),
    ppt_file: Optional[UploadFile] = File(None),
    doc_file: Optional[UploadFile] = File(None)
):
    # Validate Inputs: Require at least GitHub URL or PPT
    if not github_url and not ppt_file:
         return {
             "scores": { "innovation": 0, "quality": 0, "uiux": 0, "impact": 0 },
             "feedback": "You must provide at least a GitHub Repository URL or upload a Presentation.",
             "whyWontWin": "Because you submitted nothing."
         }

    # Validate File Type
    if ppt_file:
        filename = ppt_file.filename.lower()
        if not (filename.endswith('.ppt') or filename.endswith('.pptx') or filename.endswith('.pdf')):
             return {
                 "scores": { "innovation": 0, "quality": 0, "uiux": 0, "impact": 0 },
                 "feedback": "Invalid file type. Only .ppt, .pptx, or .pdf files are accepted.",
                 "whyWontWin": "Because you can't follow simple file format instructions."
             }

    # 1. Analyze Repo
    repo_data = {"summary": "No GitHub repository provided."}
    if github_url:
        repo_data = analyze_repo(github_url)
        
        # Check for invalid repo
        if repo_data.get("files_count", 0) == 0:
            # Generate Roast
            roast_msg = await generate_roast(github_url)
            return {
                 "scores": { "innovation": 0, "quality": 0, "uiux": 0, "impact": 0 },
                 "feedback": roast_msg,
                 "whyWontWin": "Because you didn't even submit a real project."
            }
    # else repo_data stays as default

    # 2. Analyze Video
    transcript = ""
    if video_url:
        # Extract video ID from URL
        video_id = extract_video_id(video_url)
        if video_id:
            transcript = get_video_transcript(video_id)
        else:
             transcript = "Could not extract video ID from URL."

    # 3. Analyze Docs
    doc_text = "No documents provided."
    if doc_file:
       # Placeholder for other doc types
       pass

    # 4. Analyze PPT / PDF
    ppt_text = ""
    if ppt_file:
        try:
            content = await ppt_file.read()
            filename = ppt_file.filename.lower()
            
            if filename.endswith(".pdf"):
                ppt_text = extract_text_from_pdf(content)
            else:
                # Assume PPT/PPTX
                ppt_text = extract_text_from_ppt(content)
                
        except Exception as e:
            ppt_text = f"Error reading presentation file: {e}"

    # 5. Judge
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

    analysis_result = await evaluate_project(repo_data.get("summary", ""), transcript, doc_text, ppt_text, persona)
    
    # Check if analysis_result is already a dict (error from judge_engine)
    if isinstance(analysis_result, dict):
        return {
            "scores": { "innovation": 0, "technical": 0, "relevance": 0, "uiux": 0, "impact": 0, "presentation": 0 },
            "feedback": f"Error during analysis: {analysis_result.get('error')}",
            "whyWontWin": "N/A",
            "win_probability": 0
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
            "whyWontWin": data.get("why_it_wont_win", "N/A"),
            "win_probability": data.get("win_probability", 0),
            "project_roadmap": data.get("project_roadmap", []),
            "security_issues": repo_data.get("security_issues", []),
            "ppt_analysis": data.get("ppt_analysis", {}),
            "video_analysis": data.get("video_analysis", {}),
            "languages": repo_data.get("languages", "Unknown"),
            "files_count": repo_data.get("files_count", 0),
            "judge_name": data.get("judge_name", "AI Judge")
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
