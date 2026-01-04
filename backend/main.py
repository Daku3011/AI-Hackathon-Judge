"""
AI Hackathon Judge - Backend API
--------------------------------
This is the main entry point for the FastAPI backend. It handles:
- Project Analysis (GitHub, Video, Documents)
- AI Evaluation (Gemini 1.5 Flash)
- Frontend Asset Serving
- Static File Management

Author: Dwarkesh Ramani & Team
Version: 1.1.3
"""

import sys
import os
import json
import multiprocessing
from typing import Optional

# Third-party imports
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Local imports
from services.github_analyzer import analyze_repo
from services.video_analyzer import (
    get_video_transcript, 
    extract_video_id, 
    analyze_video_quality, 
    download_video_audio, 
    upload_to_gemini, 
    fetch_transcript_with_ytdlp
)
from services.doc_analyzer import extract_text_from_pdf
from services.judge_engine import evaluate_project, generate_roast
from services.ppt_analyzer import extract_text_from_ppt

# Load environment variables
load_dotenv()

# ==========================================
# Configuration & Setup
# ==========================================

# Read version from VERSION file
VERSION = "1.1.3"
try:
    version_path = os.path.join(os.path.dirname(__file__), "VERSION")
    with open(version_path, "r") as f:
        VERSION = f.read().strip()
except (FileNotFoundError, IOError):
    pass

app = FastAPI(
    title="AI Project Judge",
    version=VERSION,
    description="An AI-powered tool that analyzes your GitHub repository and demo video to provide instant scores, feedback, and a reality check."
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Static Asset Management
# ==========================================

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
    # Check 2: Local dev relative path
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

# ==========================================
# Data Models
# ==========================================

class ProjectSubmission(BaseModel):
    github_url: str
    video_url: Optional[str] = None
    persona: Optional[str] = "standard"

# ==========================================
# API Routes
# ==========================================

@app.get("/api")
def read_root():
    """Health check endpoint."""
    return {
        "message": "AI Project Judge API is running",
        "version": VERSION
    }

@app.post("/analyze")
async def analyze_project(
    github_url: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    manual_transcript: Optional[str] = Form(None),
    persona: str = Form("standard"),
    ppt_file: Optional[UploadFile] = File(None),
    doc_file: Optional[UploadFile] = File(None)
):
    """
    Main analysis endpoint. 
    Aggregates data from GitHub, Video (YouTube/Upload), and Documents 
    to provide a comprehensive project evaluation.
    """
    
    # ---------------------------------------------------------
    # 0. Validation
    # ---------------------------------------------------------
    if not github_url and not ppt_file and not manual_transcript and not video_url:
         return {
             "scores": { "innovation": 0, "quality": 0, "uiux": 0, "impact": 0 },
             "feedback": "You must provide a GitHub URL, a Presentation, or a Video/Transcript.",
             "whyWontWin": "Because you submitted literally nothing."
         }

    if ppt_file:
        filename = ppt_file.filename.lower()
        if not (filename.endswith('.ppt') or filename.endswith('.pptx') or filename.endswith('.pdf')):
             return {
                 "scores": { "innovation": 0, "quality": 0, "uiux": 0, "impact": 0 },
                 "feedback": "Invalid file type. Only .ppt, .pptx, or .pdf files are accepted.",
                 "whyWontWin": "Because you can't follow simple file format instructions."
             }

    # ---------------------------------------------------------
    # 1. Analyze Repository
    # ---------------------------------------------------------
    repo_data = {"summary": "No GitHub repository provided."}
    if github_url:
        repo_data = analyze_repo(github_url)
        
        # Check for invalid repo (empty or non-existent)
        if repo_data.get("files_count", 0) == 0:
            roast_msg = await generate_roast(github_url)
            return {
                 "scores": { "innovation": 0, "quality": 0, "uiux": 0, "impact": 0 },
                 "feedback": roast_msg,
                 "whyWontWin": "Because you didn't even submit a real project."
            }

    # ---------------------------------------------------------
    # 2. Analyze Video / Transcript
    # ---------------------------------------------------------
    transcript = ""
    video_metadata = {}
    gemini_file_obj = None  # Handle for native video file if needed
    
    if manual_transcript and len(manual_transcript.strip()) > 50:
        # Case A: User manually pasted transcript (Highest Priority / Most Reliable)
        print("INFO: Using manual transcript provided by user.")
        transcript = manual_transcript
        video_metadata = analyze_video_quality(transcript)
        video_metadata["available"] = True
        video_metadata["quality_notes"] = "Manually provided transcript."
        
    elif video_url:
        # Case B: Fetch from YouTube
        video_id = extract_video_id(video_url)
        if video_id:
            print(f"INFO: Extracted video ID: {video_id}")
            
            # B1. Try Standard API (Fast)
            transcript = get_video_transcript(video_id)
            video_metadata = analyze_video_quality(transcript)
            print(f"DEBUG: Initial Video metadata: {video_metadata}")
            
            # B2. Fallback: yt-dlp Text Discovery (Fast)
            if not video_metadata.get("available", False):
                print("WARN: Standard transcript failed. Trying yt-dlp text fetch (Fast)...")
                ytdlp_transcript = fetch_transcript_with_ytdlp(video_url)
                
                if ytdlp_transcript:
                    print("INFO: yt-dlp text fetch successful.")
                    transcript = ytdlp_transcript
                    # Re-analyze with new text
                    video_metadata = analyze_video_quality(transcript)
                    video_metadata["available"] = True
                    video_metadata["quality_notes"] = "Recovered via yt-dlp (Fast Text Fetch)"
            
            # B3. Deep Fallback: Native Video Analysis (Slow but Powerful)
            if not video_metadata.get("available", False):
                print("WARN: Text-only methods failed. Switch to Native Video Analysis (Download -> Gemini)...")
                
                video_file_path = download_video_audio(video_url)
                
                if video_file_path:
                    # Upload to Gemini for multimodal analysis
                    gemini_file_obj = upload_to_gemini(video_file_path)
                    
                    if gemini_file_obj:
                        video_metadata["available"] = True
                        video_metadata["quality_notes"] = "Analyzed natively via Gemini (Multimodal)"
                        transcript = "[Video analyzed natively by Gemini. Original transcript unavailable.]"
                        print("INFO: Native Video Analysis setup complete.")
                        
                    # Cleanup local temp file
                    try:
                        if os.path.exists(video_file_path):
                            os.remove(video_file_path)
                    except Exception as e:
                        print(f"WARN: Cleanup warning: {e}")
                else:
                    print("ERROR: Video download failed.")
            
        else:
            transcript = "[Invalid YouTube URL: Could not extract video ID.]"
            video_metadata = {"available": False, "quality_notes": "Invalid URL"}

    # ---------------------------------------------------------
    # 3. Analyze Documents
    # ---------------------------------------------------------
    doc_text = "No documents provided."
    if doc_file:
       # Placeholder for future doc types
       pass

    # ---------------------------------------------------------
    # 4. Analyze Presentation (PPTX/PDF)
    # ---------------------------------------------------------
    ppt_text = ""
    if ppt_file:
        try:
            content = await ppt_file.read()
            filename = ppt_file.filename.lower()
            
            if filename.endswith(".pdf"):
                ppt_text = extract_text_from_pdf(content)
            else:
                ppt_text = extract_text_from_ppt(content)
                
        except Exception as e:
            ppt_text = f"Error reading presentation file: {e}"

    # ---------------------------------------------------------
    # 5. AI Evaluation (The Judge)
    # ---------------------------------------------------------
    if not os.getenv("GEMINI_API_KEY"):
         # Return Mock Response if API Key is missing
         return {
            "scores": {
                "innovation": 8, "technical": 7, "relevance": 9, 
                "uiux": 9, "impact": 8, "presentation": 7
            },
            "strengths": ["Clean project structure", "Good use of modern frameworks", "Clear documentation"],
            "improvements": ["Add more unit tests", "Improve error handling", "Add a demo video"],
            "questions": ["How do you handle scalability?", "What was the biggest technical challenge?"],
            "feedback": "Gemini API Key missing. Returning demo feedback.\n\nThe project structure looks good.",
            "whyWontWin": "The UI is basic. Adding animations would help."
         }

    analysis_result = await evaluate_project(
        repo_data.get("summary", ""), 
        transcript, 
        doc_text, 
        ppt_text, 
        persona, 
        video_metadata, 
        gemini_file_obj
    )
    
    # Handle logic errors from the engine
    if isinstance(analysis_result, dict):
        return {
            "scores": { "innovation": 0, "technical": 0, "relevance": 0, "uiux": 0, "impact": 0, "presentation": 0 },
            "feedback": f"Error during analysis: {analysis_result.get('error')}",
            "whyWontWin": "N/A",
            "win_probability": 0
        }

    # Parse JSON output from AI
    try:
        data = json.loads(analysis_result)

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
    """Fallback route to serve the React SPA."""
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found"}

if __name__ == "__main__":
    # Windows PyInstaller support
    multiprocessing.freeze_support()
    
    print(f"Starting Project Judge v{VERSION}...")
    print(f"Serving frontend from: {frontend_dist}")
    
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False, workers=1)
