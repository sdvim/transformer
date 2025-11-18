from typing import Any, Dict, List, Optional

import httpx

from transformer.config import lastfm_settings
from transformer.utils.errors import ClientError, TransientError
from transformer.utils.logging import get_logger
from transformer.utils.retry import create_retry_decorator

logger = get_logger(__name__)
retry = create_retry_decorator()


class LastFMAPI:
    """Last.fm API client for fetching user data."""

    BASE_URL = "https://ws.audioscrobbler.com/2.0/"

    def __init__(self, api_key: Optional[str] = None, username: Optional[str] = None):
        """
        Initialize Last.fm API client.

        Args:
            api_key: Last.fm API key (defaults to config)
            username: Last.fm username (defaults to config)
        """
        self.api_key = api_key or lastfm_settings.api_key
        self.username = username or lastfm_settings.user
        self.client = httpx.Client(timeout=30.0)

        if not self.api_key:
            raise ValueError("Last.fm API key is required. Set LASTFM_API_KEY in .env")

    @retry
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Last.fm API.

        Args:
            params: Query parameters for the API request

        Returns:
            JSON response from the API

        Raises:
            ClientError: If the request fails
            TransientError: If there's a temporary network issue
        """
        params["api_key"] = self.api_key
        params["format"] = "json"

        logger.info("lastfm_api_request", method=params.get("method"), user=params.get("user"))

        try:
            response = self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 503):
                raise TransientError(f"Rate limited: {e}")
            raise ClientError(f"HTTP error: {e}")
        except httpx.TimeoutException:
            raise TransientError("Request timeout")

        data = response.json()

        # Check for API errors
        if "error" in data:
            error_msg = data.get("message", "Unknown error")
            raise ClientError(f"Last.fm API error: {error_msg}")

        return data

    def get_top_artists(
        self, username: Optional[str] = None, period: str = "overall", limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get user's top artists.

        Args:
            username: Last.fm username (defaults to configured user)
            period: Time period (overall, 7day, 1month, 3month, 6month, 12month)
            limit: Number of artists to return (max 1000)

        Returns:
            List of artist dictionaries with name, playcount, and URL
        """
        user = username or self.username
        if not user:
            raise ValueError("Username is required. Set LASTFM_USER in .env or pass as argument")

        params = {"method": "user.gettopartists", "user": user, "period": period, "limit": limit}

        data = self._make_request(params)

        artists = []
        topartists = data.get("topartists", {})
        artist_list = topartists.get("artist", [])

        for artist in artist_list:
            artists.append(
                {
                    "artist": artist.get("name", ""),
                    "playcount": artist.get("playcount", "0"),
                    "url": artist.get("url", ""),
                    "mbid": artist.get("mbid", ""),
                }
            )

        logger.info("lastfm_api_complete", method="gettopartists", artists=len(artists))
        return artists

    def get_recent_tracks(
        self, username: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get user's recent tracks.

        Args:
            username: Last.fm username (defaults to configured user)
            limit: Number of tracks to return (max 200)

        Returns:
            List of track dictionaries with name, artist, album, and timestamp
        """
        user = username or self.username
        if not user:
            raise ValueError("Username is required. Set LASTFM_USER in .env or pass as argument")

        params = {"method": "user.getrecenttracks", "user": user, "limit": limit}

        data = self._make_request(params)

        tracks = []
        recenttracks = data.get("recenttracks", {})
        track_list = recenttracks.get("track", [])

        for track in track_list:
            # Skip currently playing track (has @attr nowplaying)
            if "@attr" in track and track["@attr"].get("nowplaying") == "true":
                continue

            tracks.append(
                {
                    "track": track.get("name", ""),
                    "artist": track.get("artist", {}).get("#text", ""),
                    "album": track.get("album", {}).get("#text", ""),
                    "timestamp": track.get("date", {}).get("uts", ""),
                    "url": track.get("url", ""),
                }
            )

        logger.info("lastfm_api_complete", method="getrecenttracks", tracks=len(tracks))
        return tracks

    def get_loved_tracks(
        self, username: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get user's loved tracks.

        Args:
            username: Last.fm username (defaults to configured user)
            limit: Number of tracks to return (max 1000)

        Returns:
            List of track dictionaries with name, artist, and URL
        """
        user = username or self.username
        if not user:
            raise ValueError("Username is required. Set LASTFM_USER in .env or pass as argument")

        params = {"method": "user.getlovedtracks", "user": user, "limit": limit}

        data = self._make_request(params)

        tracks = []
        lovedtracks = data.get("lovedtracks", {})
        track_list = lovedtracks.get("track", [])

        for track in track_list:
            tracks.append(
                {
                    "track": track.get("name", ""),
                    "artist": track.get("artist", {}).get("name", ""),
                    "url": track.get("url", ""),
                    "date": track.get("date", {}).get("uts", ""),
                }
            )

        logger.info("lastfm_api_complete", method="getlovedtracks", tracks=len(tracks))
        return tracks

    def get_user_info(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user information.

        Args:
            username: Last.fm username (defaults to configured user)

        Returns:
            Dictionary with user information
        """
        user = username or self.username
        if not user:
            raise ValueError("Username is required. Set LASTFM_USER in .env or pass as argument")

        params = {"method": "user.getinfo", "user": user}

        data = self._make_request(params)

        user_data = data.get("user", {})
        return {
            "name": user_data.get("name", ""),
            "realname": user_data.get("realname", ""),
            "playcount": user_data.get("playcount", "0"),
            "country": user_data.get("country", ""),
            "url": user_data.get("url", ""),
            "registered": user_data.get("registered", {}).get("unixtime", ""),
        }

    def __del__(self):
        """Close the HTTP client when done."""
        if hasattr(self, "client"):
            self.client.close()
