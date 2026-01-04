"""
Video Analyzer Service
----------------------
Handles all interactions regarding video content analysis:
1. Transcript Fetching (Standard API) -> Fast, Text-only
2. Transcript Fetching (yt-dlp fallback) -> Fast, Text-only, Robust
3. Native Video Analysis (yt-dlp download -> Gemini) -> Slow, Multimodal (Audio+Visual)

Author: Dwarkesh Ramani & Team
"""

import os
import time
import hashlib
import json
import re
from pathlib import Path
from typing import Optional

# Third-party imports
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from google import genai
from google.genai import types

# ==========================================
# Configuration
# ==========================================

CACHE_DIR = Path(os.getenv("TRANSCRIPT_CACHE_DIR", "/tmp/transcript_cache"))
CACHE_EXPIRY_SECONDS = int(os.getenv("TRANSCRIPT_CACHE_EXPIRY", 86400))  # 24 hours default

# ==========================================
# Caching System
# ==========================================

def _get_cache_path(video_id: str) -> Path:
    """Generate cache file path for a video ID."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_key = hashlib.sha256(video_id.encode()).hexdigest()
    return CACHE_DIR / f"{cache_key}.json"

def _get_cached_transcript(video_id: str) -> Optional[str]:
    """Retrieve cached transcript if available and not expired."""
    try:
        cache_path = _get_cache_path(video_id)
        if not cache_path.exists():
            return None
        
        # Check if cache is expired
        cache_age = time.time() - cache_path.stat().st_mtime
        if cache_age > CACHE_EXPIRY_SECONDS:
            try:
                cache_path.unlink()  # Delete expired cache
            except (OSError, PermissionError) as e:
                print(f"WARN: Failed to delete expired cache file: {e}")
            return None
        
        with open(cache_path, 'r') as f:
            data = json.load(f)
            return data.get('transcript')
    except Exception as e:
        print(f"ERROR: Cache read error: {e}")
        return None

def _cache_transcript(video_id: str, transcript: str):
    """Cache transcript to disk."""
    try:
        cache_path = _get_cache_path(video_id)
        with open(cache_path, 'w') as f:
            json.dump({'transcript': transcript, 'video_id': video_id}, f)
    except Exception as e:
        print(f"ERROR: Cache write error: {e}")

# ==========================================
# ID Extraction & Utilities
# ==========================================

def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the video ID from a YouTube URL.
    Supports standard, short (youtu.be), and embed URLs.
    """
    if not url or not isinstance(url, str):
        return None
    
    # Strip whitespace
    url = url.strip()
    
    # Regex patterns for different YouTube URL formats
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([^#\&\?]*).*'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Validate video ID length (should be 11 characters)
            if len(video_id) == 11:
                return video_id
    
    return None

def analyze_video_quality(transcript: str) -> dict:
    """
    Analyze the quality of video transcript for presentation metrics.
    Retruns metrics including word count, estimated duration, filler words.
    """
    if not transcript or transcript.startswith("[Transcript unavailable"):
        return {
            "available": False,
            "word_count": 0,
            "estimated_duration_minutes": 0,
            "avg_words_per_minute": 0,
            "quality_notes": "Transcript not available"
        }
    
    # Basic metrics
    words = transcript.split()
    word_count = len(words)
    
    # Estimate speaking duration (average speaking rate: 130-150 words/minute)
    avg_speaking_rate = 140
    estimated_duration = word_count / avg_speaking_rate
    
    # Detect potential filler words using word boundaries
    filler_words = ['um', 'uh', 'like', 'you know', 'so', 'basically', 'actually', 'literally']
    filler_count = 0
    
    # Use word boundaries to avoid false positives
    transcript_lower = transcript.lower()
    words_list = transcript_lower.split()
    
    for word in filler_words:
        if ' ' in word:
            # Multi-word filler phrase - count occurrences in word list by joining
            # Split into individual words and search for the sequence
            phrase_words = word.split()
            phrase_len = len(phrase_words)
            for i in range(len(words_list) - phrase_len + 1):
                if words_list[i:i+phrase_len] == phrase_words:
                    filler_count += 1
        else:
            # Single word - count exact matches
            filler_count += words_list.count(word)
    
    filler_percentage = (filler_count / word_count * 100) if word_count > 0 else 0
    
    quality_notes = []
    if word_count < 100:
        quality_notes.append("Very short presentation")
    elif word_count > 2000:
        quality_notes.append("Very long presentation")
    
    if filler_percentage > 5:
        quality_notes.append(f"High filler word usage ({filler_percentage:.1f}%)")
    
    return {
        "available": True,
        "word_count": word_count,
        "estimated_duration_minutes": round(estimated_duration, 1),
        "avg_words_per_minute": avg_speaking_rate,
        "filler_word_count": filler_count,
        "filler_percentage": round(filler_percentage, 2),
        "quality_notes": "; ".join(quality_notes) if quality_notes else "Good quality transcript"
    }

# ==========================================
# Method 1: Standard API (youtube-transcript-api)
# ==========================================

def get_video_transcript(video_id: str, max_retries: int = 3, timeout: int = 30):
    """
    Fetch transcript for a YouTube video with retry logic and caching.
    Uses official (unofficial) API which is fast but often blocked.
    """
    if not video_id:
        return "[Transcript unavailable: Invalid video ID.]"
    
    # Check cache first
    cached = _get_cached_transcript(video_id)
    if cached:
        print(f"INFO: Using cached transcript for video: {video_id}")
        return cached
    
    # Configuration for bypass
    proxies = None
    proxy_url = os.getenv("YOUTUBE_PROXY")
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}
        print(f"INFO: Using proxy: {proxy_url}")
        
    cookies = None
    cookies_file = os.getenv("YOUTUBE_COOKIES_FILE")
    if cookies_file and os.path.exists(cookies_file):
        cookies = cookies_file
        print(f"INFO: Using cookies file: {cookies_file}")
    
    # Retry loop
    for attempt in range(max_retries):
        try:
            print(f"DEBUG: Fetching transcript for video {video_id} (attempt {attempt + 1}/{max_retries})")
            
            # Set timeout for the operation
            start_time = time.time()
            
            transcript_text = _fetch_transcript_with_timeout(video_id, proxies, cookies, timeout)
            
            elapsed = time.time() - start_time
            print(f"INFO: Transcript fetched successfully in {elapsed:.2f}s")
            
            # Cache the successful result
            _cache_transcript(video_id, transcript_text)
            
            return transcript_text
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"WARN: Transcript not available: {str(e)}")
            return "[Transcript unavailable: Captions are disabled or missing for this video.]"
            
        except Exception as e:
            print(f"WARN: Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt)  # 1s, 2s, 4s
                print(f"DEBUG: Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                error_msg = f"[Transcript unavailable after {max_retries} attempts: {str(e)}]"
                print(error_msg)
                return error_msg
    
    return "[Transcript unavailable: All attempts failed.]"

def _fetch_transcript_with_timeout(video_id: str, proxies: Optional[dict], cookies: Optional[str], timeout: int) -> str:
    """Internal helper to interact with YouTubeTranscriptApi."""
    
    ytt_api = YouTubeTranscriptApi()
    transcript_obj = None
    
    # Modern API (list_transcripts)
    if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
        try:
            transcript_list = ytt_api.list_transcripts(video_id, proxies=proxies, cookies=cookies)
            
            try:
                # Prioritize English
                transcript_obj = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                print("DEBUG: Found English transcript")
            except:
                # Next best: Translate
                try:
                    first_transcript = next(iter(transcript_list))
                    if first_transcript.is_translatable:
                        print(f"DEBUG: Translating transcript from {first_transcript.language_code} to English")
                        transcript_obj = first_transcript.translate('en')
                    else:
                        print(f"DEBUG: Using non-English transcript: {first_transcript.language_code}")
                        transcript_obj = first_transcript
                except StopIteration:
                    raise NoTranscriptFound(video_id, [], None)
                    
        except Exception as e:
            print(f"WARN: Transcript list failed (Modern API): {e}")
            # Fall through to try direct fetch
    
    # If we got a transcript object, fetch it
    if transcript_obj:
        fetched = transcript_obj.fetch()
        text = " ".join([entry['text'] for entry in fetched])
        return text
    
    # Fallback: legacy fetch
    print("DEBUG: Attempting direct transcript fetch...")
    
    if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
        # Modern API direct fetch
        raw_transcript = ytt_api.get_transcript(video_id, proxies=proxies, cookies=cookies)
    else:
        # Legacy API (Thread safety warnings applied)
        print("WARN: Using Legacy YouTubeTranscriptApi.")
        
        # Env var hack for legacy proxy support
        old_http = os.environ.get("HTTP_PROXY")
        old_https = os.environ.get("HTTPS_PROXY")
        
        if proxies and proxies.get("http"):
            os.environ["HTTP_PROXY"] = proxies["http"]
            os.environ["HTTPS_PROXY"] = proxies.get("https", proxies["http"])

        try:
            raw_transcript = ytt_api.fetch(video_id)
        finally:
            # Restore env
            if proxies:
                if old_http is None:
                    os.environ.pop("HTTP_PROXY", None)
                else:
                    os.environ["HTTP_PROXY"] = old_http
                if old_https is None:
                    os.environ.pop("HTTPS_PROXY", None)
                else:
                    os.environ["HTTPS_PROXY"] = old_https
    
    # Parse format
    if raw_transcript and (isinstance(raw_transcript, list) or hasattr(raw_transcript, '__iter__')):
        transcript_items = list(raw_transcript)
        
        if len(transcript_items) > 0:
            if isinstance(transcript_items[0], dict):
                text = " ".join([entry.get('text', '') for entry in transcript_items])
            else:
                text_parts = []
                for entry in transcript_items:
                    if hasattr(entry, 'text'):
                        text_parts.append(entry.text)
                text = " ".join(text_parts)
            
            if text:
                return text
    
    raise Exception("Failed to extract transcript text from API response")


# ==========================================
# Method 2: yt-dlp Transcript Fetch (Fast Fallback)
# ==========================================

def fetch_transcript_with_ytdlp(video_url: str) -> Optional[str]:
    """
    Fetches transcript using yt-dlp (no video download).
    Robust against 'Subtitles disabled' errors from other APIs.
    """
    try:
        if not video_url:
            return None
            
        print(f"INFO: Attempting yt-dlp transcript fetch for {video_url}...")
        
        # Use a temp directory
        sub_dir = Path("/tmp/ytdlp_subs")
        sub_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        out_tmpl = str(sub_dir / f"sub_{timestamp}_%(id)s")
        
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'outtmpl': out_tmpl,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=True)
            
            # Find the created file
            expected_prefix = f"sub_{timestamp}_"
            
            latest_file = None
            for f in sub_dir.iterdir():
                if f.name.startswith(expected_prefix) and f.suffix in ['.vtt', '.srt']:
                    latest_file = f
                    break
            
            if latest_file:
                print(f"INFO: Found subtitle file via yt-dlp: {latest_file.name}")
                content = latest_file.read_text(errors='ignore')
                latest_file.unlink() # Cleanup
                return content
            
            print("INFO: No subtitle file created by yt-dlp.")
            return None
            
    except Exception as e:
        print(f"WARN: yt-dlp transcript fetch failed: {e}")
        return None


# ==========================================
# Method 3: Native Video Analysis (Download -> Gemini)
# ==========================================

def download_video_audio(video_url: str) -> Optional[str]:
    """
    Downloads video/audio from YouTube using yt-dlp.
    Returns the path to the downloaded file.
    """
    try:
        if not video_url:
            return None

        # Create temp directory
        download_path = Path("/tmp/video_downloads")
        download_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        output_template = str(download_path / f"video_{timestamp}_%(id)s.%(ext)s")
        
        ydl_opts = {
            'format': 'best[height<=480]/best',  # Limit resolution to 480p to be fast
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"INFO: Downloading video from {video_url}...")
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"INFO: Video downloaded to: {filename}")
            return filename
            
    except Exception as e:
        print(f"ERROR: Download failed: {e}")
        return None

def upload_to_gemini(file_path: str) -> Optional[types.File]:
    """
    Uploads a file to Gemini API and waits for processing.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Missing GEMINI_API_KEY")
        return None
        
    try:
        client = genai.Client(api_key=api_key)
        
        print(f"INFO: Uploading {file_path} to Gemini...")
        file_obj = client.files.upload(file=file_path)
        print(f"INFO: Uploaded: {file_obj.name}")
        
        # Wait for processing
        while file_obj.state.name == "PROCESSING":
            print("DEBUG: Processing video file on Gemini...")
            time.sleep(2)
            file_obj = client.files.get(name=file_obj.name)
            
        if file_obj.state.name == "FAILED":
            print("ERROR: Gemini failed to process the video file.")
            return None
            
        print(f"INFO: Video ready for analysis: {file_obj.uri}")
        return file_obj
        
    except Exception as e:
        print(f"ERROR: Gemini upload failed: {e}")
        return None
