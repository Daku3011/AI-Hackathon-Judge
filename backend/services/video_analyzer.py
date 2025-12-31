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
        
        transcript_obj = None
        
        # 1. Try to list all transcripts
        try:
            transcript_list = ytt_api.list(video_id)
            
            # 2. Try to find English or auto-generated English
            try:
                transcript_obj = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
            except:
                # 3. If no English, try to translate the first available transcript
                try:
                    first_transcript = next(iter(transcript_list))
                    if first_transcript.is_translatable:
                        transcript_obj = first_transcript.translate('en')
                    else:
                        transcript_obj = first_transcript
                except:
                    pass
        except Exception as e:
            # If list fails, fall back to direct fetch (legacy/simple mode)
            print(f"Transcript list failed: {e}")
            pass

        # 4. If we still don't have an object, try direct fetch as last resort
        if not transcript_obj:
             # fetch returns a list of dictionaries/objects directly in this lib version apparently
             # based on previous code: transcript = ytt_api.fetch(video_id)
             # "returns iterable FetchedTranscript object" <- comment from original code
             # But if list() failed, fetch() might be the only way if it's a different API structure than expected?
             # Let's rely on the previous simple fetch if the complex one failed
             raw_transcript = ytt_api.fetch(video_id)
             text = " ".join([entry.text for entry in raw_transcript])
             return text
        else:
             # If we got a transcript object from list/find/translate
             fetched = transcript_obj.fetch()
             text = " ".join([entry.text for entry in fetched])
             return text

    except (TranscriptsDisabled, NoTranscriptFound):
        return "[Transcript unavailable: Captions are disabled or missing.]"
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return "[Transcript unavailable: Technical error during retrieval.]"
