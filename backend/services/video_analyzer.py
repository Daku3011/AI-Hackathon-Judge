from youtube_transcript_api import YouTubeTranscriptApi

def get_video_transcript(video_id: str):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([Entry['text'] for Entry in transcript])
        return text
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"
