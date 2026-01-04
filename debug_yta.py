from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print(f"Has list_transcripts: {hasattr(YouTubeTranscriptApi, 'list_transcripts')}")
print(f"Has get_transcript: {hasattr(YouTubeTranscriptApi, 'get_transcript')}")
print(f"Dir: {dir(YouTubeTranscriptApi)}")

try:
    api = YouTubeTranscriptApi()
    print("Instantiation successful")
except Exception as e:
    print(f"Instantiation failed: {e}")
