import os
from unittest.mock import Mock, patch

import pytest

from transformer.scrapers.lastfm_api import LastFMAPI
from transformer.utils.errors import ClientError


@pytest.fixture
def api_key():
    """Return test API key."""
    return os.getenv("LASTFM_API_KEY", "test_api_key")


@pytest.fixture
def username():
    """Return test username."""
    return os.getenv("LASTFM_USER", "test_user")


@pytest.fixture
def mock_top_artists_response():
    """Mock response for user.gettopartists."""
    return {
        "topartists": {
            "artist": [
                {
                    "name": "Test Artist 1",
                    "playcount": "1000",
                    "url": "https://www.last.fm/music/Test+Artist+1",
                    "mbid": "test-mbid-1",
                },
                {
                    "name": "Test Artist 2",
                    "playcount": "500",
                    "url": "https://www.last.fm/music/Test+Artist+2",
                    "mbid": "test-mbid-2",
                },
            ]
        }
    }


@pytest.fixture
def mock_recent_tracks_response():
    """Mock response for user.getrecenttracks."""
    return {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track 1",
                    "artist": {"#text": "Test Artist 1"},
                    "album": {"#text": "Test Album 1"},
                    "date": {"uts": "1234567890"},
                    "url": "https://www.last.fm/music/Test+Artist+1/_/Test+Track+1",
                },
                {
                    "name": "Test Track 2",
                    "artist": {"#text": "Test Artist 2"},
                    "album": {"#text": "Test Album 2"},
                    "date": {"uts": "1234567891"},
                    "url": "https://www.last.fm/music/Test+Artist+2/_/Test+Track+2",
                },
            ]
        }
    }


@pytest.fixture
def mock_user_info_response():
    """Mock response for user.getinfo."""
    return {
        "user": {
            "name": "test_user",
            "realname": "Test User",
            "playcount": "10000",
            "country": "United States",
            "url": "https://www.last.fm/user/test_user",
            "registered": {"unixtime": "1000000000"},
        }
    }


def test_lastfm_api_initialization(api_key, username):
    """Test LastFMAPI initialization."""
    api = LastFMAPI(api_key=api_key, username=username)
    assert api.api_key == api_key
    assert api.username == username


def test_lastfm_api_initialization_from_config():
    """Test LastFMAPI initialization from config."""
    # Should use values from .env file
    api = LastFMAPI()
    assert api.api_key is not None
    assert api.username is not None


def test_lastfm_api_missing_api_key():
    """Test that ValueError is raised when API key is missing."""
    with patch("transformer.scrapers.lastfm_api.lastfm_settings") as mock_settings:
        mock_settings.api_key = None
        with pytest.raises(ValueError, match="API key is required"):
            LastFMAPI(api_key=None, username="test_user")


def test_get_top_artists_mock(api_key, username, mock_top_artists_response):
    """Test get_top_artists with mocked response."""
    with patch("httpx.Client.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_top_artists_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = LastFMAPI(api_key=api_key, username=username)
        artists = api.get_top_artists()

        assert len(artists) == 2
        assert artists[0]["artist"] == "Test Artist 1"
        assert artists[0]["playcount"] == "1000"
        assert artists[1]["artist"] == "Test Artist 2"
        assert artists[1]["playcount"] == "500"


def test_get_recent_tracks_mock(api_key, username, mock_recent_tracks_response):
    """Test get_recent_tracks with mocked response."""
    with patch("httpx.Client.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_recent_tracks_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = LastFMAPI(api_key=api_key, username=username)
        tracks = api.get_recent_tracks()

        assert len(tracks) == 2
        assert tracks[0]["track"] == "Test Track 1"
        assert tracks[0]["artist"] == "Test Artist 1"
        assert tracks[1]["track"] == "Test Track 2"
        assert tracks[1]["artist"] == "Test Artist 2"


def test_get_user_info_mock(api_key, username, mock_user_info_response):
    """Test get_user_info with mocked response."""
    with patch("httpx.Client.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_user_info_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = LastFMAPI(api_key=api_key, username=username)
        user_info = api.get_user_info()

        assert user_info["name"] == "test_user"
        assert user_info["realname"] == "Test User"
        assert user_info["playcount"] == "10000"


def test_api_error_handling(api_key, username):
    """Test that API errors are properly handled."""
    error_response = {"error": 6, "message": "User not found"}

    with patch("httpx.Client.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = error_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = LastFMAPI(api_key=api_key, username=username)

        with pytest.raises(ClientError, match="User not found"):
            api.get_top_artists()


@pytest.mark.skipif(
    not os.getenv("LASTFM_API_KEY"), reason="LASTFM_API_KEY not set - skipping live API test"
)
def test_lastfm_api_live():
    """
    Test Last.fm API with live request.

    This test only runs if LASTFM_API_KEY is set in environment.
    It makes a real API call to verify the integration works.
    """
    api = LastFMAPI()

    # Test get_top_artists
    artists = api.get_top_artists(limit=5)
    assert isinstance(artists, list)
    assert len(artists) > 0
    assert "artist" in artists[0]
    assert "playcount" in artists[0]

    print(f"\n✓ Successfully fetched {len(artists)} top artists")
    print(f"  Top artist: {artists[0]['artist']} ({artists[0]['playcount']} plays)")

    # Test get_recent_tracks
    tracks = api.get_recent_tracks(limit=5)
    assert isinstance(tracks, list)
    assert len(tracks) > 0
    assert "track" in tracks[0]
    assert "artist" in tracks[0]

    print(f"✓ Successfully fetched {len(tracks)} recent tracks")
    print(f"  Latest track: {tracks[0]['track']} by {tracks[0]['artist']}")

    # Test get_user_info
    user_info = api.get_user_info()
    assert isinstance(user_info, dict)
    assert "name" in user_info
    assert "playcount" in user_info

    print(f"✓ Successfully fetched user info")
    print(f"  User: {user_info['name']} ({user_info['playcount']} total plays)")


@pytest.mark.skipif(
    not os.getenv("LASTFM_API_KEY"), reason="LASTFM_API_KEY not set - skipping integration test"
)
def test_lastfm_scraper_with_api():
    """
    Test that LastFMScraper uses API when credentials are available.

    This test verifies the integration between LastFMScraper and LastFMAPI.
    """
    from transformer.scrapers.lastfm import LastFMScraper

    scraper = LastFMScraper()
    username = os.getenv("LASTFM_USER", "sdvim")

    # This should use the API
    results = scraper.scrape(f"https://www.last.fm/user/{username}")

    assert isinstance(results, list)
    assert len(results) > 0
    assert "artist" in results[0]
    assert "playcount" in results[0]

    print(f"\n✓ LastFMScraper successfully used API")
    print(f"  Fetched {len(results)} artists")
    print(f"  Top artist: {results[0]['artist']} ({results[0]['playcount']} plays)")
