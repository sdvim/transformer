#!/usr/bin/env python3
"""Test script to demonstrate YouTube API functionality."""

import sys

from transformer.scrapers.youtube_api import YouTubeAPI

# Example playlist URLs for testing
EXAMPLE_PLAYLISTS = {
    "small": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",  # Small playlist for quick testing
    "music": "PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI",  # Music playlist example
}

EXAMPLE_VIDEOS = {
    "first_youtube": "jNQXAC9IVRw",  # "Me at the zoo" - first YouTube video
    "test": "dQw4w9WgXcQ",  # Well-known test video
}


def test_playlist(api: YouTubeAPI, playlist_id: str, max_results: int = 5):
    """Test playlist fetching."""
    print(f"\nTesting Playlist: {playlist_id}")
    print("=" * 70)

    videos = api.get_playlist_items(playlist_id, max_results=max_results)

    print(f"\n✓ Successfully fetched {len(videos)} videos\n")

    for i, video in enumerate(videos, 1):
        duration = api.format_duration(video["duration"]) if video.get("duration") else "N/A"
        views = int(video.get("view_count", 0))

        print(f"{i}. {video['title']}")
        print(f"   Channel: {video['channel']}")
        print(f"   Duration: {duration}")
        print(f"   Views: {views:,}")
        print(f"   Video ID: {video['video_id']}")
        print()


def test_video(api: YouTubeAPI, video_id: str):
    """Test single video fetching."""
    print(f"\nTesting Video: {video_id}")
    print("=" * 70)

    video_info = api.get_video_info(video_id)

    duration = api.format_duration(video_info["duration"])
    views = int(video_info["view_count"])
    likes = int(video_info["like_count"])

    print(f"\n✓ Successfully fetched video info\n")
    print(f"Title: {video_info['title']}")
    print(f"Channel: {video_info['channel']}")
    print(f"Duration: {duration}")
    print(f"Views: {views:,}")
    print(f"Likes: {likes:,}")
    print(f"Published: {video_info['published_at']}")
    if video_info.get("tags"):
        print(f"Tags: {', '.join(video_info['tags'][:5])}")
    print()


def test_url_parsing(api: YouTubeAPI):
    """Test URL parsing functionality."""
    print("\nTesting URL Parsing")
    print("=" * 70)

    test_urls = [
        ("https://www.youtube.com/playlist?list=PLtest123", "playlist", "PLtest123"),
        ("https://www.youtube.com/watch?v=abc123", "video", "abc123"),
        ("https://youtu.be/xyz789", "video", "xyz789"),
        (
            "https://www.youtube.com/watch?v=abc&list=PLtest456",
            "both",
            ("abc", "PLtest456"),
        ),
    ]

    print()
    for url, url_type, expected in test_urls:
        if url_type == "playlist":
            result = api.extract_playlist_id(url)
            status = "✓" if result == expected else "✗"
            print(f"{status} Playlist URL: {url}")
            print(f"   Expected: {expected}, Got: {result}")
        elif url_type == "video":
            result = api.extract_video_id(url)
            status = "✓" if result == expected else "✗"
            print(f"{status} Video URL: {url}")
            print(f"   Expected: {expected}, Got: {result}")
        elif url_type == "both":
            video_id = api.extract_video_id(url)
            playlist_id = api.extract_playlist_id(url)
            v_status = "✓" if video_id == expected[0] else "✗"
            p_status = "✓" if playlist_id == expected[1] else "✗"
            print(f"{v_status}/{p_status} Mixed URL: {url}")
            print(f"   Expected video: {expected[0]}, Got: {video_id}")
            print(f"   Expected playlist: {expected[1]}, Got: {playlist_id}")
        print()


def main():
    """Main test function."""
    print("YouTube API Test Script")
    print("=" * 70)

    try:
        api = YouTubeAPI()
        print("\n✓ API initialized successfully")
    except ValueError as e:
        print(f"\n✗ API initialization failed: {e}")
        print("\nTo run this test, you need to:")
        print("1. Get a YouTube API key from https://console.cloud.google.com/apis/credentials")
        print("2. Add it to your .env file as YOUTUBE_API_KEY=your_key_here")
        sys.exit(1)

    # Test URL parsing (doesn't require API calls)
    test_url_parsing(api)

    # Test playlist fetching
    test_playlist(api, EXAMPLE_PLAYLISTS["small"], max_results=3)

    # Test video fetching
    test_video(api, EXAMPLE_VIDEOS["first_youtube"])

    print("=" * 70)
    print("All tests completed! ✓")
    print("=" * 70)


if __name__ == "__main__":
    main()
