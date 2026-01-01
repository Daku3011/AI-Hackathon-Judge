from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

import re
from typing import Optional

import os

def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the video ID from a YouTube URL.
    Supports standard, short (youtu.be), and embed URLs.
    """
    if not url:
        return None
    
    # Regex patterns for different YouTube URL formats
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([^#\&\?]*).*'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
             return match.group(1)
    
    return None

def get_video_transcript(video_id: str):
    try:
        # Configuration for bypass
        proxies = None
        proxy_url = os.getenv("YOUTUBE_PROXY")
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}
            
        cookies = None
        cookies_file = os.getenv("YOUTUBE_COOKIES_FILE")
        if cookies_file and os.path.exists(cookies_file):
            cookies = cookies_file
            
        # Instantiate the API class
        ytt_api = YouTubeTranscriptApi()
        
        transcript_obj = None
        
        if cookies_file and os.path.exists(cookies_file):
            cookies = cookies_file
            
        # Instantiate the API class
        ytt_api = YouTubeTranscriptApi()
        
        transcript_obj = None
        
        # Check for modern API (v0.5+)
        if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
            # Modern: Pass proxies/cookies directly
            try:
                transcript_list = ytt_api.list_transcripts(video_id, proxies=proxies, cookies=cookies)
                try:
                    transcript_obj = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                except:
                    try:
                        first_transcript = next(iter(transcript_list))
                        if first_transcript.is_translatable:
                            transcript_obj = first_transcript.translate('en')
                        else:
                            transcript_obj = first_transcript
                    except:
                        pass
            except Exception as e:
                print(f"Transcript list failed (Modern): {e}")
                pass
        else:
            # Legacy: v0.4.x or older (no list_transcripts)
            # Must use os.environ for proxies as fallback
            # Cookies might not be supported easily in legacy without monkeypatching requests, so we skip cookies for legacy or rely on global
            print("Using Legacy YouTubeTranscriptApi (Update recommended)")
            
            # Set usage proxies via env vars temporarily if not set
            old_http = os.environ.get("HTTP_PROXY")
            old_https = os.environ.get("HTTPS_PROXY")
            
            if proxy_url:
                os.environ["HTTP_PROXY"] = proxy_url
                os.environ["HTTPS_PROXY"] = proxy_url

            try:
                # Legacy 'list' method
                if hasattr(ytt_api, 'list'):
                    try:
                        # ytt_api.list(video_id) returns a list of dicts: [{'text':..., 'start':..., 'duration':...}] ?? 
                        # checking previous code... it used list() then find_transcript...
                        # Wait, legacy .list() usually returned a list of transcript metadata? 
                        # Actually inspect_api said 'list' exists.
                        # Let's assume it behaves like the old .list_transcripts but returns a list of objects we can pick from?
                        # Or maybe it's just 'fetch' is the only reliable one.
                        # Let's try basic fetch first for legacy.
                        pass 
                    except:
                        pass
            except Exception as e:
                print(f"Transcript list failed (Legacy): {e}")
                
            # Cleanup Env (Optional, maybe keep it?)
            if proxy_url:
                # restore or unset
                if old_http is None: del os.environ["HTTP_PROXY"]
                else: os.environ["HTTP_PROXY"] = old_http
                if old_https is None: del os.environ["HTTPS_PROXY"]
                else: os.environ["HTTPS_PROXY"] = old_https

        # 4. If we still don't have an object, try direct fetch as last resort
        if not transcript_obj:
             # fetch logic with fallback
             try:
                if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
                     raw_transcript = ytt_api.get_transcript(video_id, proxies=proxies, cookies=cookies)
                else:
                     # Legacy Fetch
                     if proxy_url:
                        os.environ["HTTP_PROXY"] = proxy_url
                        os.environ["HTTPS_PROXY"] = proxy_url
                     
                     raw_transcript = ytt_api.fetch(video_id) # inspect_api confirmed 'fetch' exists
                     
                     if proxy_url:
                        if old_http is None: del os.environ["HTTP_PROXY"]
                        else: os.environ["HTTP_PROXY"] = old_http
                        if old_https is None: del os.environ["HTTPS_PROXY"]
                        else: os.environ["HTTPS_PROXY"] = old_https
                        
                # Handle inconsistent return types (list of dicts vs objects)
                # Legacy fetch usually returns list of dicts [{'text': '...', ...}]
                # Modern get_transcript also returns list of dicts
                if raw_transcript and isinstance(raw_transcript, list) and isinstance(raw_transcript[0], dict):
                     text = " ".join([entry.get('text', '') for entry in raw_transcript])
                else:
                     # iterate assuming object
                     text = " ".join([getattr(entry, 'text', str(entry)) for entry in raw_transcript])
                return text
                
             except Exception as e:
                print(f"Direct fetch failed: {e}")
                
        else:
             # If we got a transcript object from list/find/translate
             fetched = transcript_obj.fetch()
             text = " ".join([entry['text'] for entry in fetched])
             return text

    except (TranscriptsDisabled, NoTranscriptFound):
        return "[Transcript unavailable: Captions are disabled or missing.]"
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return f"[Transcript unavailable: {str(e)}]"
