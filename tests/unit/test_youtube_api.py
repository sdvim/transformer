import os
from unittest.mock import Mock, patch

import pytest

from transformer.scrapers.youtube_api import YouTubeAPI
from transformer.utils.errors import ClientError


@pytest.fixture
def api_key():
    """Return test API key."""
    return os.getenv("YOUTUBE_API_KEY", "test_api_key")


@pytest.fixture
def mock_playlist_response():
    """Mock response for playlistItems endpoint."""
    return {
        "items": [
            {
                "snippet": {
                    "title": "Test Video 1",
                    "channelTitle": "Test Channel",
                    "publishedAt": "2024-01-01T00:00:00Z",
                    "description": "Test description 1",
                    "thumbnails": {"default": {"url": "https://example.com/thumb1.jpg"}},
                },
                "contentDetails": {"videoId": "test_video_1"},
            },
            {
                "snippet": {
                    "title": "Test Video 2",
                    "channelTitle": "Test Channel",
                    "publishedAt": "2024-01-02T00:00:00Z",
                    "description": "Test description 2",
                    "thumbnails": {"default": {"url": "https://example.com/thumb2.jpg"}},
                },
                "contentDetails": {"videoId": "test_video_2"},
            },
        ]
    }


@pytest.fixture
def mock_video_details_response():
    """Mock response for videos endpoint (details)."""
    return {
        "items": [
            {
                "id": "test_video_1",
                "contentDetails": {"duration": "PT4M13S"},
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "100",
                    "commentCount": "10",
                },
            },
            {
                "id": "test_video_2",
                "contentDetails": {"duration": "PT10M30S"},
                "statistics": {
                    "viewCount": "5000",
                    "likeCount": "500",
                    "commentCount": "50",
                },
            },
        ]
    }


@pytest.fixture
def mock_video_info_response():
    """Mock response for single video info."""
    return {
        "items": [
            {
                "id": "test_video_1",
                "snippet": {
                    "title": "Test Video",
                    "channelTitle": "Test Channel",
                    "publishedAt": "2024-01-01T00:00:00Z",
                    "description": "Test description",
                    "tags": ["test", "video"],
                    "categoryId": "10",
                },
                "contentDetails": {"duration": "PT4M13S"},
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "100",
                    "commentCount": "10",
                },
            }
        ]
    }


def test_youtube_api_initialization(api_key):
    """Test YouTubeAPI initialization."""
    api = YouTubeAPI(api_key=api_key)
    assert api.api_key == api_key


def test_youtube_api_missing_api_key():
    """Test that ValueError is raised when API key is missing."""
    with patch("transformer.scrapers.youtube_api.youtube_settings") as mock_settings:
        mock_settings.api_key = None
        with pytest.raises(ValueError, match="API key is required"):
            YouTubeAPI(api_key=None)


def test_extract_playlist_id():
    """Test playlist ID extraction from various URL formats."""
    api = YouTubeAPI(api_key="test_key")

    # Standard format
    url1 = "https://www.youtube.com/playlist?list=PLtest123"
    assert api.extract_playlist_id(url1) == "PLtest123"

    # With video parameter
    url2 = "https://www.youtube.com/watch?v=abc123&list=PLtest456"
    assert api.extract_playlist_id(url2) == "PLtest456"


def test_extract_video_id():
    """Test video ID extraction from various URL formats."""
    api = YouTubeAPI(api_key="test_key")

    # Standard format
    url1 = "https://www.youtube.com/watch?v=abc123"
    assert api.extract_video_id(url1) == "abc123"

    # Short format
    url2 = "https://youtu.be/xyz789"
    assert api.extract_video_id(url2) == "xyz789"


def test_parse_duration():
    """Test ISO 8601 duration parsing."""
    api = YouTubeAPI(api_key="test_key")

    assert api.parse_duration("PT4M13S") == 253  # 4*60 + 13
    assert api.parse_duration("PT1H30M") == 5400  # 1*3600 + 30*60
    assert api.parse_duration("PT45S") == 45
    assert api.parse_duration("PT2H") == 7200


def test_format_duration():
    """Test duration formatting."""
    api = YouTubeAPI(api_key="test_key")

    assert api.format_duration("PT4M13S") == "4:13"
    assert api.format_duration("PT1H30M15S") == "1:30:15"
    assert api.format_duration("PT45S") == "0:45"


def test_get_playlist_items_mock(api_key, mock_playlist_response, mock_video_details_response):
    """Test get_playlist_items with mocked responses."""
    with patch("httpx.Client.get") as mock_get:
        # First call returns playlist items
        playlist_response = Mock()
        playlist_response.json.return_value = mock_playlist_response
        playlist_response.raise_for_status = Mock()

        # Second call returns video details
        details_response = Mock()
        details_response.json.return_value = mock_video_details_response
        details_response.raise_for_status = Mock()

        mock_get.side_effect = [playlist_response, details_response]

        api = YouTubeAPI(api_key=api_key)
        videos = api.get_playlist_items("PLtest123", max_results=50)

        assert len(videos) == 2
        assert videos[0]["title"] == "Test Video 1"
        assert videos[0]["video_id"] == "test_video_1"
        assert videos[0]["duration"] == "PT4M13S"
        assert videos[1]["title"] == "Test Video 2"


def test_get_video_info_mock(api_key, mock_video_info_response):
    """Test get_video_info with mocked response."""
    with patch("httpx.Client.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_video_info_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = YouTubeAPI(api_key=api_key)
        video_info = api.get_video_info("test_video_1")

        assert video_info["title"] == "Test Video"
        assert video_info["channel"] == "Test Channel"
        assert video_info["video_id"] == "test_video_1"
        assert video_info["view_count"] == "1000"
        assert "test" in video_info["tags"]


def test_api_error_handling(api_key):
    """Test that API errors are properly handled."""
    error_response = {"error": {"message": "API key not valid"}}

    with patch("httpx.Client.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = error_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = YouTubeAPI(api_key=api_key)

        with pytest.raises(ClientError, match="API key not valid"):
            api.get_playlist_items("PLtest123")


@pytest.mark.skipif(
    not os.getenv("YOUTUBE_API_KEY"), reason="YOUTUBE_API_KEY not set - skipping live API test"
)
def test_youtube_api_live_playlist():
    """
    Test YouTube API with live request for a playlist.

    This test only runs if YOUTUBE_API_KEY is set in environment.
    Uses a well-known public playlist.
    """
    api = YouTubeAPI()

    # Use YouTube's own "YouTube Rewind" playlist or similar public playlist
    # This is a small, stable playlist for testing
    playlist_id = "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"  # Example: YouTube Developers channel

    videos = api.get_playlist_items(playlist_id, max_results=5)

    assert isinstance(videos, list)
    assert len(videos) > 0
    assert "title" in videos[0]
    assert "channel" in videos[0]
    assert "video_id" in videos[0]

    print(f"\n✓ Successfully fetched {len(videos)} videos from playlist")
    print(f"  First video: {videos[0]['title']}")
    print(f"  Channel: {videos[0]['channel']}")
    if videos[0].get("duration"):
        formatted = api.format_duration(videos[0]["duration"])
        print(f"  Duration: {formatted}")


@pytest.mark.skipif(
    not os.getenv("YOUTUBE_API_KEY"), reason="YOUTUBE_API_KEY not set - skipping live API test"
)
def test_youtube_api_live_video():
    """
    Test YouTube API with live request for a single video.

    Uses a well-known stable video for testing.
    """
    api = YouTubeAPI()

    # Use a stable, well-known video (e.g., "Me at the zoo" - first YouTube video)
    video_id = "jNQXAC9IVRw"

    video_info = api.get_video_info(video_id)

    assert isinstance(video_info, dict)
    assert video_info["video_id"] == video_id
    assert "title" in video_info
    assert "channel" in video_info
    assert "view_count" in video_info

    print(f"\n✓ Successfully fetched video info")
    print(f"  Title: {video_info['title']}")
    print(f"  Channel: {video_info['channel']}")
    print(f"  Views: {video_info['view_count']}")


@pytest.mark.skipif(
    not os.getenv("YOUTUBE_API_KEY"), reason="YOUTUBE_API_KEY not set - skipping integration test"
)
def test_youtube_scraper_with_api():
    """
    Test that YouTubeScraper uses API when credentials are available.
    """
    from transformer.scrapers.youtube import YouTubeScraper

    scraper = YouTubeScraper()

    # Use a short, stable playlist
    playlist_url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

    results = scraper.scrape(playlist_url)

    assert isinstance(results, list)
    assert len(results) > 0
    assert "title" in results[0]
    assert "channel" in results[0]

    print(f"\n✓ YouTubeScraper successfully used API")
    print(f"  Fetched {len(results)} videos")
    print(f"  First video: {results[0]['title']}")
