"""
DEBUG UTILITY: yt-dlp Subtitle Fetcher
--------------------------------------
This is a developer utility used to verify that yt-dlp can find English subtitles
on a specific YouTube video without downloading it.

Usage:
    This script is not part of the production pipeline.
    Run manually if you need to debug transcript fetching:
    $ python debug_ytdlp_subs.py
"""

import yt_dlp
import json
import sys

def get_subs_stdout(url):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            print("Title:", info.get('title'))
            
            # Check for subtitles
            subs = info.get('subtitles') or info.get('automatic_captions')
            if subs and 'en' in subs:
                print("Found English subtitles.")
                return True
            else:
                print("No English subtitles found.")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

# Disabled by default in production imports
if __name__ == "__main__":
    # Change URL to test different videos
    url = "https://www.youtube.com/watch?v=t2Nn06u8Krg"
    get_subs_stdout(url)
