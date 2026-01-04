from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

import re
from typing import Optional
import os
import time
import hashlib
import json
from pathlib import Path

# Cache directory for video transcripts
CACHE_DIR = Path(os.getenv("TRANSCRIPT_CACHE_DIR", "/tmp/transcript_cache"))
CACHE_EXPIRY_SECONDS = int(os.getenv("TRANSCRIPT_CACHE_EXPIRY", 86400))  # 24 hours default

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
                print(f"Failed to delete expired cache file: {e}")
            return None
        
        with open(cache_path, 'r') as f:
            data = json.load(f)
            return data.get('transcript')
    except Exception as e:
        print(f"Cache read error: {e}")
        return None

def _cache_transcript(video_id: str, transcript: str):
    """Cache transcript to disk."""
    try:
        cache_path = _get_cache_path(video_id)
        with open(cache_path, 'w') as f:
            json.dump({'transcript': transcript, 'video_id': video_id}, f)
    except Exception as e:
        print(f"Cache write error: {e}")

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

def get_video_transcript(video_id: str, max_retries: int = 3, timeout: int = 30):
    """
    Fetch transcript for a YouTube video with retry logic and caching.
    
    Args:
        video_id: YouTube video ID
        max_retries: Maximum number of retry attempts
        timeout: Timeout in seconds for each attempt
    
    Returns:
        str: Transcript text or error message
    """
    if not video_id:
        return "[Transcript unavailable: Invalid video ID.]"
    
    # Check cache first
    cached = _get_cached_transcript(video_id)
    if cached:
        print(f"Using cached transcript for video: {video_id}")
        return cached
    
    # Configuration for bypass
    proxies = None
    proxy_url = os.getenv("YOUTUBE_PROXY")
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}
        print(f"Using proxy: {proxy_url}")
        
    cookies = None
    cookies_file = os.getenv("YOUTUBE_COOKIES_FILE")
    if cookies_file and os.path.exists(cookies_file):
        cookies = cookies_file
        print(f"Using cookies file: {cookies_file}")
    
    # Retry loop
    for attempt in range(max_retries):
        try:
            print(f"Fetching transcript for video {video_id} (attempt {attempt + 1}/{max_retries})")
            
            # Set timeout for the operation
            start_time = time.time()
            
            transcript_text = _fetch_transcript_with_timeout(video_id, proxies, cookies, timeout)
            
            elapsed = time.time() - start_time
            print(f"Transcript fetched successfully in {elapsed:.2f}s")
            
            # Cache the successful result
            _cache_transcript(video_id, transcript_text)
            
            return transcript_text
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"Transcript not available: {str(e)}")
            return "[Transcript unavailable: Captions are disabled or missing for this video.]"
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            
            # If this isn't the last attempt, wait before retrying (exponential backoff)
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt)  # 1s, 2s, 4s
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                # Last attempt failed
                error_msg = f"[Transcript unavailable after {max_retries} attempts: {str(e)}]"
                print(error_msg)
                return error_msg
    
    return "[Transcript unavailable: All attempts failed.]"

def _fetch_transcript_with_timeout(video_id: str, proxies: Optional[dict], cookies: Optional[str], timeout: int) -> str:
    """
    Internal function to fetch transcript with proper error handling.
    
    Args:
        video_id: YouTube video ID
        proxies: Proxy configuration
        cookies: Cookies file path
        timeout: Timeout in seconds (note: youtube-transcript-api doesn't support timeout directly)
    
    Returns:
        str: Transcript text
    """
    # Instantiate the API class
    ytt_api = YouTubeTranscriptApi()
    
    transcript_obj = None
    
    # Check for modern API (v0.5+)
    if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
        # Modern: Pass proxies/cookies directly
        try:
            transcript_list = ytt_api.list_transcripts(video_id, proxies=proxies, cookies=cookies)
            
            # Try to find English transcript first
            try:
                transcript_obj = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                print("Found English transcript")
            except:
                # Try to get any available transcript and translate if needed
                try:
                    first_transcript = next(iter(transcript_list))
                    if first_transcript.is_translatable:
                        print(f"Translating transcript from {first_transcript.language_code} to English")
                        transcript_obj = first_transcript.translate('en')
                    else:
                        print(f"Using non-English transcript: {first_transcript.language_code}")
                        transcript_obj = first_transcript
                except StopIteration:
                    raise NoTranscriptFound(video_id, [], None)
                    
        except Exception as e:
            print(f"Transcript list failed (Modern API): {e}")
            # Fall through to try direct fetch
    
    # If we got a transcript object, fetch it
    if transcript_obj:
        fetched = transcript_obj.fetch()
        text = " ".join([entry['text'] for entry in fetched])
        return text
    
    # Fallback: try direct fetch
    print("Attempting direct transcript fetch...")
    
    if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
        # Modern API direct fetch
        raw_transcript = ytt_api.get_transcript(video_id, proxies=proxies, cookies=cookies)
    else:
        # Legacy API (v0.4.x or older)
        print("Using Legacy YouTubeTranscriptApi (Update recommended)")
        print("WARNING: Legacy API may have thread-safety issues in multi-threaded environments")
        
        # IMPORTANT NOTE: The legacy API requires setting environment variables for proxy
        # support, which creates race conditions in multi-threaded environments (e.g., 
        # uvicorn with multiple workers). For production deployments:
        # 1. Upgrade to youtube-transcript-api >= 0.5.0 (recommended)
        # 2. Use single-worker mode (workers=1) if using legacy API
        # 3. Avoid proxy configuration if possible with legacy API
        
        # Set proxies via env vars temporarily (with mutex-like finally block)
        old_http = os.environ.get("HTTP_PROXY")
        old_https = os.environ.get("HTTPS_PROXY")
        
        if proxies and proxies.get("http"):
            os.environ["HTTP_PROXY"] = proxies["http"]
            os.environ["HTTPS_PROXY"] = proxies.get("https", proxies["http"])

        try:
            raw_transcript = ytt_api.fetch(video_id)
        finally:
            # Always restore env vars to minimize race condition window
            if proxies:
                if old_http is None:
                    os.environ.pop("HTTP_PROXY", None)
                else:
                    os.environ["HTTP_PROXY"] = old_http
                if old_https is None:
                    os.environ.pop("HTTPS_PROXY", None)
                else:
                    os.environ["HTTPS_PROXY"] = old_https
    
    # Handle response format
    # Allow iterables like FetchedTranscript
    if raw_transcript and (isinstance(raw_transcript, list) or hasattr(raw_transcript, '__iter__')):
        # Convert to list to safely check length and first element
        transcript_items = list(raw_transcript)
        
        if len(transcript_items) > 0:
            if isinstance(transcript_items[0], dict):
                text = " ".join([entry.get('text', '') for entry in transcript_items])
            else:
                # Handle object format (FetchedTranscriptSnippet)
                text_parts = []
                for entry in transcript_items:
                    if hasattr(entry, 'text'):
                        text_parts.append(entry.text)
                    else:
                        print(f"WARNING: Transcript entry missing 'text' attribute: {type(entry)}")
                text = " ".join(text_parts)
            
            if text:
                return text
    
    raise Exception("Failed to extract transcript text from API response")

def analyze_video_quality(transcript: str) -> dict:
    """
    Analyze the quality of video transcript for presentation metrics.
    
    Args:
        transcript: Video transcript text
    
    Returns:
        dict: Analysis metrics including word count, estimated duration, etc.
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
