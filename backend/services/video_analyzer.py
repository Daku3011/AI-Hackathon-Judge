"""
Video Analyzer Service (Production-Safe)
---------------------------------------
1. youtube-transcript-api (fast)
2. yt-dlp subtitles (one-time fallback)
3. Gemini multimodal analysis (optional)

Cloud-safe (Render compatible)
Author: Dwarkesh Ramani & Team
"""

import os
import time
import json
import re
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any

import yt_dlp
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
from google import genai
from google.genai import types

# ======================================================
# Configuration
# ======================================================

CACHE_DIR = Path(os.getenv("TRANSCRIPT_CACHE_DIR", "/tmp/transcript_cache"))
CACHE_EXPIRY = int(os.getenv("TRANSCRIPT_CACHE_EXPIRY", 86400))      # 24h
BLOCK_EXPIRY = int(os.getenv("TRANSCRIPT_BLOCK_EXPIRY", 21600))      # 6h
VIDEO_MODE = os.getenv("VIDEO_MODE", "full")                         # safe | balanced | full

CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# Cache Helpers
# ======================================================

def _cache_path(video_id: str) -> Path:
    key = hashlib.sha256(video_id.encode()).hexdigest()
    return CACHE_DIR / f"{key}.json"


def load_cache(video_id: str) -> Optional[Dict]:
    path = _cache_path(video_id)
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text())
        age = time.time() - data.get("timestamp", 0)

        if data.get("status") == "blocked" and age < BLOCK_EXPIRY:
            return data

        if age > CACHE_EXPIRY:
            path.unlink(missing_ok=True)
            return None

        return data
    except Exception:
        return None


def save_cache(video_id: str, payload: Dict):
    payload["timestamp"] = time.time()
    _cache_path(video_id).write_text(json.dumps(payload))


# ======================================================
# Utilities
# ======================================================

def extract_video_id(url: str) -> Optional[str]:
    if not url:
        return None
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None


def clean_subtitle_text(text: str) -> str:
    text = re.sub(r"\d+:\d+:\d+\.\d+ --> .*", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n+", " ", text)
    return text.strip()


# ======================================================
# Transcript Quality
# ======================================================

def analyze_transcript_quality(transcript: str) -> Dict:
    if not transcript:
        return {"available": False}

    words = transcript.split()
    wc = len(words)
    duration = round(wc / 140, 1)

    fillers = {"um", "uh", "like", "basically", "actually"}
    filler_count = sum(words.count(f) for f in fillers)

    return {
        "available": True,
        "word_count": wc,
        "estimated_minutes": duration,
        "filler_percentage": round((filler_count / wc) * 100, 2) if wc else 0,
    }


# ======================================================
# Method 1: youtube-transcript-api
# ======================================================

def fetch_transcript_api(video_id: str) -> Optional[str]:
    try:
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(d["text"] for d in data)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception:
        return None


# ======================================================
# Method 2: yt-dlp subtitles (ONE TRY ONLY)
# ======================================================

def fetch_transcript_ytdlp(video_url: str) -> Optional[str]:
    try:
        tmp = Path("/tmp/ytdlp_subs")
        tmp.mkdir(exist_ok=True)

        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "outtmpl": str(tmp / "%(id)s.%(ext)s"),
            "quiet": True,
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(video_url, download=True)

        for f in tmp.iterdir():
            if f.suffix in (".vtt", ".srt"):
                text = clean_subtitle_text(f.read_text(errors="ignore"))
                f.unlink(missing_ok=True)
                return text

    except Exception:
        return None

    return None


# ======================================================
# Method 3: Gemini Multimodal (FULL MODE ONLY)
# ======================================================

def analyze_with_gemini(video_url: str) -> Optional[Any]:
    """
    Downloads video and uploads to Gemini.
    Returns: types.File object or None
    """
    # Force full mode if explicit call
    # if VIDEO_MODE != "full":
    #    return None

    try:
        tmp = Path("/tmp/video")
        tmp.mkdir(exist_ok=True)

        ydl_opts = {
            "format": "best[height<=480]/best",
            "outtmpl": str(tmp / "%(id)s.%(ext)s"),
            "quiet": True,
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        }

        print(f"INFO: Downloading video for Native Analysis: {video_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

        print(f"INFO: Uploading to Gemini: {file_path}")
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        file_obj = client.files.upload(file=file_path)

        start = time.time()
        while file_obj.state.name == "PROCESSING":
            if time.time() - start > 120:
                print("WARN: Gemini processing timeout")
                break
            time.sleep(2)
            file_obj = client.files.get(name=file_obj.name)

        # Cleanup
        try:
            os.remove(file_path)
        except:
            pass
            
        return file_obj

    except Exception as e:
        print(f"ERROR: Native analysis failed: {e}")
        return None


# ======================================================
# Main Orchestrator
# ======================================================

def analyze_video(video_url: str) -> Dict:
    """
    Central function to specific strategy.
    Returns dict with keys: 
    - method: 'api' | 'yt-dlp' | 'gemini'
    - transcript: str (for text methods)
    - quality: dict (metadata)
    - gemini_file: types.File (for gemini method)
    - error: str (if blocked/failed)
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}

    # cached = load_cache(video_id)
    # if cached:
    #     return cached

    print(f"DEBUG: orchestrating video analysis for {video_id}")

    # Step 1: API transcript
    print("DEBUG: Trying Method 1 (Standard API)...")
    transcript = fetch_transcript_api(video_id)
    if transcript:
        return {
            "method": "api",
            "transcript": transcript,
            "quality": analyze_transcript_quality(transcript),
        }

    # Step 2: yt-dlp (balanced/full)
    print("DEBUG: Trying Method 2 (yt-dlp)...")
    transcript = fetch_transcript_ytdlp(video_url)
    if transcript:
        return {
            "method": "yt-dlp",
            "transcript": transcript,
            "quality": analyze_transcript_quality(transcript),
        }

    # Step 3: Gemini
    print("DEBUG: Trying Method 3 (Native Gemini)...")
    gemini_file = analyze_with_gemini(video_url)
    if gemini_file:
        return {
            "method": "gemini", 
            "gemini_file": gemini_file,
            "quality": {"available": True, "quality_notes": "Native Video Analysis"}
        }

    # Blocked
    return {
        "status": "blocked",
        "error": "Transcript unavailable. Upload video or screenshots.",
    }
