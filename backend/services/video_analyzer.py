"""
Video Analyzer Service (Browser-Assisted / Render-Safe)
---------------------------------------
1. youtube-transcript-api (lightweight, optional fallback)
2. Browser-provided transcript (PRIMARY)

No yt-dlp. No headless browser. No IP blocking issues.
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
VIDEO_MODE = os.getenv("VIDEO_MODE", "full")                         # Default back to full

CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# Cache Helpers
# ======================================================

def _get_cache_path(video_id: str) -> Path:
    return CACHE_DIR / f"{video_id}.json"

def _get_cached_transcript(video_id: str) -> Optional[str]:
    cache_path = _get_cache_path(video_id)
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cached_time = data.get("timestamp", 0)
        if time.time() - cached_time < CACHE_EXPIRY:
            return data.get("transcript")
    except Exception as e:
        print(f"DEBUG: Cache read error for {video_id}: {e}")
    return None

def _cache_transcript(video_id: str, transcript: str):
    try:
        cache_path = _get_cache_path(video_id)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({
                "video_id": video_id,
                "transcript": transcript,
                "timestamp": time.time()
            }, f)
    except Exception as e:
        print(f"DEBUG: Cache write error for {video_id}: {e}")

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

def analyze_transcript_quality(transcript: str) -> Dict[str, Any]:
    if not transcript or not transcript.strip():
        return {"available": False, "word_count": 0, "quality_notes": "No transcript provided"}

    if transcript.strip().startswith("[Analysis Failed") or transcript.strip().startswith("[Transcript unavailable"):
        return {"available": False, "word_count": 0, "quality_notes": "Transcript unavailable"}

    words = transcript.split()
    wc = len(words)
    if wc == 0:
        return {"available": False, "word_count": 0, "quality_notes": "Empty transcript"}

    duration = round(wc / 140, 1)

    fillers = {"um", "uh", "like", "basically", "actually"}
    filler_count = sum(words.count(f) for f in fillers)
    filler_pct = round((filler_count / wc) * 100, 2) if wc else 0

    quality_notes = []
    if wc < 50:
        quality_notes.append("Very short presentation")
    if filler_pct > 5:
        quality_notes.append("High filler word usage")
    elif filler_pct < 2:
        quality_notes.append("Clean speech, low filler words")

    notes_str = "; ".join(quality_notes) if quality_notes else "Standard presentation delivery"

    return {
        "available": True,
        "word_count": wc,
        "estimated_minutes": duration,
        "estimated_duration_minutes": duration,
        "avg_words_per_minute": 140,
        "filler_word_count": filler_count,
        "filler_percentage": filler_pct,
        "quality_notes": notes_str
    }

# Backward compatibility alias
analyze_video_quality = analyze_transcript_quality

# ======================================================
# Method 1: youtube-transcript-api (Server-side Fallback)
# ======================================================

def get_cookies_file() -> Optional[str]:
    """
    Locates the cookies.txt file for authenticated requests.
    Checks:
    1. ENV VAR: YOUTUBE_COOKIES_FILE
    2. Local: cookies.txt (in root or backend)
    3. Render Secret: /etc/secrets/cookies.txt
    """
    env_path = os.getenv("YOUTUBE_COOKIES_FILE")
    if env_path and os.path.exists(env_path):
        return env_path
        
    candidates = [
        "cookies.txt",
        "backend/cookies.txt",
        "/etc/secrets/cookies.txt",
        "/app/cookies.txt"
    ]
    
    for path in candidates:
        if os.path.exists(path):
            print(f"DEBUG: Found cookies file at {path}")
            return path
            
    return None

def fetch_transcript_api(video_id: str) -> Optional[str]:
    try:
        cookies = get_cookies_file()
        
        if cookies:
            try:
                import http.cookiejar
                cj = http.cookiejar.MozillaCookieJar(cookies)
                cj.load()
                print(f"DEBUG: Successfully loaded {len(cj)} cookies from file.")
            except Exception as e:
                print(f"ERROR: Cookie file found but failed to load: {e}")

            print(f"INFO: Fetching transcript with cookies auth: {cookies}")
            data = YouTubeTranscriptApi.get_transcript(video_id, cookies=cookies)
        else:
            print("INFO: Fetching transcript (No cookies found, might be blocked)")
            data = YouTubeTranscriptApi.get_transcript(video_id)
            
        return " ".join(d["text"] for d in data)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        print(f"WARN: API Transcript fetch failed: {e}")
        return None


import shutil
import uuid

# ======================================================
# Method 2: yt-dlp subtitles (ONE TRY ONLY)
# ======================================================

def fetch_transcript_ytdlp(video_url: str) -> Optional[str]:
    tmp_path = Path(f"/tmp/ytdlp_subs_{uuid.uuid4()}")
    try:
        tmp_path.mkdir(parents=True, exist_ok=True)
        
        cookies_path = get_cookies_file()

        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "outtmpl": str(tmp_path / "%(id)s.%(ext)s"),
            "quiet": True,
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        }
        
        if cookies_path:
            print(f"INFO: yt-dlp using cookies from {cookies_path}")
            opts["cookiefile"] = cookies_path

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(video_url, download=True)

        for f in tmp_path.iterdir():
            if f.suffix in (".vtt", ".srt"):
                text = clean_subtitle_text(f.read_text(errors="ignore"))
                return text

    except Exception as e:
        print(f"WARN: yt-dlp failed: {e}")
        return None
    finally:
        # Cleanup unique directory
        if tmp_path.exists():
            shutil.rmtree(tmp_path, ignore_errors=True)

    return None


# ======================================================
# Method 3: Gemini Multimodal (FULL MODE ONLY)
# ======================================================

def analyze_with_gemini(video_url: str) -> Optional[Any]:
    """
    Downloads video and uploads to Gemini.
    Returns: types.File object or None
    """
    tmp_path = Path(f"/tmp/video_{uuid.uuid4()}")
    try:
        tmp_path.mkdir(parents=True, exist_ok=True)
        
        cookies_path = get_cookies_file()

        ydl_opts = {
            "format": "best[height<=480]/best",
            "outtmpl": str(tmp_path / "%(id)s.%(ext)s"),
            "quiet": True,
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        }
        
        if cookies_path:
            ydl_opts["cookiefile"] = cookies_path

        print(f"INFO: Downloading video for Native Analysis: {video_url}")
        file_path = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)

        if not file_path or not os.path.exists(file_path):
             print("ERROR: file not found after download")
             return None

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
            
        return file_obj

    except Exception as e:
        print(f"ERROR: Native analysis failed: {e}")
        return None
    finally:
         # Cleanup unique directory
        if tmp_path.exists():
            shutil.rmtree(tmp_path, ignore_errors=True)



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

    print(f"DEBUG: orchestrating video analysis for {video_id}")

    # Step 0: Check transcript cache
    cached_transcript = _get_cached_transcript(video_id)
    if cached_transcript:
        print(f"INFO: Using cached transcript for {video_id}")
        return {
            "method": "cache",
            "transcript": cached_transcript,
            "quality": analyze_transcript_quality(cached_transcript),
        }

    # Step 1: API transcript
    print("DEBUG: Trying Method 1 (Standard API)...")
    transcript = fetch_transcript_api(video_id)
    if transcript:
        _cache_transcript(video_id, transcript)
        return {
            "method": "api",
            "transcript": transcript,
            "quality": analyze_transcript_quality(transcript),
        }

    # Step 2: yt-dlp (balanced/full ONLY)
    if VIDEO_MODE in ("balanced", "full"):
        print("DEBUG: Trying Method 2 (yt-dlp)...")
        transcript = fetch_transcript_ytdlp(video_url)
        if transcript:
            _cache_transcript(video_id, transcript)
            return {
                "method": "yt-dlp",
                "transcript": transcript,
                "quality": analyze_transcript_quality(transcript),
            }

    # Step 3: Gemini (full ONLY)
    if VIDEO_MODE == "full":
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
        "error": "Transcript unavailable (All methods failed). Local: Check cookies.txt. Cloud: IP Blocked.",
    }
