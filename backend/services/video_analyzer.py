from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

import re
from typing import Optional

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
        # Instantiate the API class
        ytt_api = YouTubeTranscriptApi()
        
        # Fetch transcript (returns iterable FetchedTranscript object)
        transcript = ytt_api.fetch(video_id)
        
        # Extract text from snippets
        text = " ".join([entry.text for entry in transcript])
        return text
    except (TranscriptsDisabled, NoTranscriptFound):
        return "[No transcript available for this video. Enable captions on YouTube if possible.]"
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"
