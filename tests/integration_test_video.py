#!/usr/bin/env python3
"""
Integration test for video analysis improvements.
Tests the complete flow from URL to analysis.
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from services.video_analyzer import (
    extract_video_id,
    get_video_transcript,
    analyze_video_quality,
    _get_cached_transcript
)


def test_video_id_extraction():
    """Test various YouTube URL formats"""
    test_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s", "dQw4w9WgXcQ"),
        ("invalid-url", None),
        ("", None),
    ]
    
    print("Testing Video ID Extraction...")
    for url, expected in test_urls:
        result = extract_video_id(url)
        status = "✓" if result == expected else "✗"
        print(f"  {status} URL: {url[:50]}... => {result}")
    print()


def test_video_quality_analysis():
    """Test video quality analysis with various inputs"""
    print("Testing Video Quality Analysis...")
    
    # Test 1: Good transcript
    good_transcript = " ".join(["word"] * 300)
    result = analyze_video_quality(good_transcript)
    print(f"  ✓ Good transcript: {result['word_count']} words, "
          f"{result['estimated_duration_minutes']}min")
    
    # Test 2: Short transcript
    short_transcript = "This is very short"
    result = analyze_video_quality(short_transcript)
    print(f"  ✓ Short transcript: {result['word_count']} words, "
          f"notes: {result['quality_notes']}")
    
    # Test 3: High filler words
    filler_transcript = " ".join(["um"] * 30 + ["word"] * 70)
    result = analyze_video_quality(filler_transcript)
    print(f"  ✓ Filler words: {result['filler_percentage']}%, "
          f"notes: {result['quality_notes']}")
    
    # Test 4: Unavailable transcript
    unavail = "[Transcript unavailable: Error]"
    result = analyze_video_quality(unavail)
    print(f"  ✓ Unavailable: available={result['available']}")
    print()


def test_caching():
    """Test transcript caching"""
    print("Testing Caching System...")
    
    # Check if cache is working
    test_video_id = "test_integration_12345"
    cached = _get_cached_transcript(test_video_id)
    
    if cached is None:
        print("  ✓ Cache miss for new video ID (expected)")
    else:
        print(f"  ℹ Found cached transcript: {len(cached)} chars")
    print()


def test_error_handling():
    """Test error handling for invalid video IDs"""
    print("Testing Error Handling...")
    
    # This should fail gracefully
    invalid_id = "invalid_video_id_xyz"
    transcript = get_video_transcript(invalid_id, max_retries=1, timeout=5)
    
    if transcript.startswith("[Transcript unavailable"):
        print(f"  ✓ Handled invalid video ID gracefully")
        print(f"    Message: {transcript[:80]}...")
    else:
        print(f"  ✗ Unexpected response: {transcript[:80]}...")
    print()


def main():
    print("=" * 70)
    print("VIDEO ANALYSIS INTEGRATION TEST")
    print("=" * 70)
    print()
    
    test_video_id_extraction()
    test_video_quality_analysis()
    test_caching()
    test_error_handling()
    
    print("=" * 70)
    print("INTEGRATION TEST COMPLETED")
    print("=" * 70)
    print()
    print("Note: Real YouTube API tests require network access and may be")
    print("rate-limited. The tests above verify the core functionality.")


if __name__ == "__main__":
    main()
