import unittest
from unittest.mock import MagicMock, patch, Mock
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from services.video_analyzer import (
    extract_video_id,
    analyze_video_quality,
    _get_cached_transcript,
    _cache_transcript
)


class TestVideoAnalyzer(unittest.TestCase):
    
    def test_extract_video_id_standard_url(self):
        """Test extracting video ID from standard YouTube URL"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = extract_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    def test_extract_video_id_short_url(self):
        """Test extracting video ID from short youtu.be URL"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = extract_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    def test_extract_video_id_embed_url(self):
        """Test extracting video ID from embed URL"""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = extract_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    def test_extract_video_id_with_params(self):
        """Test extracting video ID from URL with additional parameters"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtu.be"
        video_id = extract_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    def test_extract_video_id_invalid_url(self):
        """Test handling of invalid URL"""
        url = "https://example.com/video"
        video_id = extract_video_id(url)
        self.assertIsNone(video_id)
    
    def test_extract_video_id_empty_url(self):
        """Test handling of empty URL"""
        video_id = extract_video_id("")
        self.assertIsNone(video_id)
    
    def test_extract_video_id_none(self):
        """Test handling of None URL"""
        video_id = extract_video_id(None)
        self.assertIsNone(video_id)
    
    def test_analyze_video_quality_good_transcript(self):
        """Test video quality analysis with a good transcript"""
        transcript = " ".join(["word"] * 300)  # 300 words
        result = analyze_video_quality(transcript)
        
        self.assertTrue(result["available"])
        self.assertEqual(result["word_count"], 300)
        self.assertGreater(result["estimated_duration_minutes"], 0)
        self.assertEqual(result["avg_words_per_minute"], 140)
    
    def test_analyze_video_quality_short_transcript(self):
        """Test video quality analysis with short transcript"""
        transcript = "This is a very short video"
        result = analyze_video_quality(transcript)
        
        self.assertTrue(result["available"])
        self.assertIn("Very short presentation", result["quality_notes"])
    
    def test_analyze_video_quality_with_filler_words(self):
        """Test video quality analysis detects filler words"""
        transcript = " ".join(["um"] * 20 + ["word"] * 80)  # 20% filler words
        result = analyze_video_quality(transcript)
        
        self.assertTrue(result["available"])
        self.assertGreater(result["filler_percentage"], 5)
        self.assertIn("High filler word usage", result["quality_notes"])
    
    def test_analyze_video_quality_unavailable(self):
        """Test video quality analysis with unavailable transcript"""
        transcript = "[Transcript unavailable: Error message]"
        result = analyze_video_quality(transcript)
        
        self.assertFalse(result["available"])
        self.assertEqual(result["word_count"], 0)
    
    def test_analyze_video_quality_empty(self):
        """Test video quality analysis with empty transcript"""
        result = analyze_video_quality("")
        
        self.assertFalse(result["available"])
        self.assertEqual(result["word_count"], 0)
    
    def test_cache_operations(self):
        """Test caching and retrieval of transcripts"""
        video_id = "test_video_123"
        transcript = "This is a test transcript for caching."
        
        # Cache the transcript
        _cache_transcript(video_id, transcript)
        
        # Retrieve from cache
        cached = _get_cached_transcript(video_id)
        
        self.assertEqual(cached, transcript)


if __name__ == '__main__':
    unittest.main()
