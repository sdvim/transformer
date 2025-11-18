"""YouTube Data API v3 client for fetching video and playlist data."""

from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import httpx

from transformer.config import youtube_settings
from transformer.utils.errors import ClientError, TransientError
from transformer.utils.logging import get_logger
from transformer.utils.retry import create_retry_decorator

logger = get_logger(__name__)
retry = create_retry_decorator()


class YouTubeAPI:
    """YouTube Data API v3 client for fetching video and playlist data."""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube API client.

        Args:
            api_key: YouTube API key (defaults to config)
        """
        self.api_key = api_key or youtube_settings.api_key
        self.client = httpx.Client(timeout=30.0)

        if not self.api_key:
            raise ValueError(
                "YouTube API key is required. Set YOUTUBE_API_KEY in .env or get one at "
                "https://console.cloud.google.com/apis/credentials"
            )

    @retry
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the YouTube API.

        Args:
            endpoint: API endpoint (e.g., "playlistItems", "videos")
            params: Query parameters for the API request

        Returns:
            JSON response from the API

        Raises:
            ClientError: If the request fails
            TransientError: If there's a temporary network issue
        """
        params["key"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"

        logger.info("youtube_api_request", endpoint=endpoint, params=list(params.keys()))

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 503):
                raise TransientError(f"Rate limited: {e}")
            error_data = e.response.json() if e.response.text else {}
            error_msg = error_data.get("error", {}).get("message", str(e))
            raise ClientError(f"YouTube API error: {error_msg}")
        except httpx.TimeoutException:
            raise TransientError("Request timeout")

        data = response.json()

        # Check for API errors
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            raise ClientError(f"YouTube API error: {error_msg}")

        return data

    def extract_playlist_id(self, url: str) -> Optional[str]:
        """
        Extract playlist ID from YouTube URL.

        Args:
            url: YouTube playlist URL

        Returns:
            Playlist ID or None if not found
        """
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        # Try list parameter
        if "list" in query_params:
            return query_params["list"][0]

        return None

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.

        Args:
            url: YouTube video URL

        Returns:
            Video ID or None if not found
        """
        parsed = urlparse(url)

        # Standard youtube.com/watch?v=
        if parsed.hostname in ("www.youtube.com", "youtube.com"):
            query_params = parse_qs(parsed.query)
            if "v" in query_params:
                return query_params["v"][0]

        # Short youtu.be/ format
        if parsed.hostname == "youtu.be":
            return parsed.path.lstrip("/")

        return None

    def get_playlist_items(self, playlist_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get items from a YouTube playlist.

        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of items to return (max 50 per page)

        Returns:
            List of video dictionaries with title, channel, duration, etc.
        """
        logger.info("fetching_playlist", playlist_id=playlist_id)

        videos = []
        page_token = None

        while len(videos) < max_results:
            params = {
                "part": "snippet,contentDetails",
                "playlistId": playlist_id,
                "maxResults": min(50, max_results - len(videos)),
            }

            if page_token:
                params["pageToken"] = page_token

            data = self._make_request("playlistItems", params)

            items = data.get("items", [])
            if not items:
                break

            # Extract video IDs to get additional details
            video_ids = [item["contentDetails"]["videoId"] for item in items]

            # Fetch video details for duration, view count, etc.
            video_details = self.get_video_details(video_ids)

            for item in items:
                snippet = item["snippet"]
                video_id = item["contentDetails"]["videoId"]
                details = video_details.get(video_id, {})

                videos.append(
                    {
                        "title": snippet.get("title", ""),
                        "channel": snippet.get("channelTitle", ""),
                        "video_id": video_id,
                        "duration": details.get("duration", ""),
                        "view_count": details.get("view_count", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "description": snippet.get("description", ""),
                        "thumbnail": snippet.get("thumbnails", {})
                        .get("default", {})
                        .get("url", ""),
                    }
                )

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        logger.info("playlist_fetch_complete", videos=len(videos))
        return videos

    def get_video_details(self, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get details for multiple videos.

        Args:
            video_ids: List of video IDs

        Returns:
            Dictionary mapping video ID to details
        """
        if not video_ids:
            return {}

        params = {
            "part": "contentDetails,statistics",
            "id": ",".join(video_ids),
        }

        data = self._make_request("videos", params)

        details = {}
        for item in data.get("items", []):
            video_id = item["id"]
            content = item.get("contentDetails", {})
            stats = item.get("statistics", {})

            details[video_id] = {
                "duration": content.get("duration", ""),
                "view_count": stats.get("viewCount", "0"),
                "like_count": stats.get("likeCount", "0"),
                "comment_count": stats.get("commentCount", "0"),
            }

        return details

    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get information about a single video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with video information
        """
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
        }

        data = self._make_request("videos", params)

        items = data.get("items", [])
        if not items:
            raise ClientError(f"Video not found: {video_id}")

        item = items[0]
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        stats = item.get("statistics", {})

        return {
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "video_id": video_id,
            "duration": content.get("duration", ""),
            "view_count": stats.get("viewCount", "0"),
            "like_count": stats.get("likeCount", "0"),
            "comment_count": stats.get("commentCount", "0"),
            "published_at": snippet.get("publishedAt", ""),
            "description": snippet.get("description", ""),
            "tags": snippet.get("tags", []),
            "category_id": snippet.get("categoryId", ""),
        }

    def parse_duration(self, duration: str) -> int:
        """
        Parse ISO 8601 duration to seconds.

        Args:
            duration: ISO 8601 duration string (e.g., "PT4M13S")

        Returns:
            Duration in seconds
        """
        import re

        pattern = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
        match = pattern.match(duration)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    def format_duration(self, duration: str) -> str:
        """
        Format ISO 8601 duration to human-readable format.

        Args:
            duration: ISO 8601 duration string

        Returns:
            Formatted duration (e.g., "4:13")
        """
        total_seconds = self.parse_duration(duration)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"

    def __del__(self):
        """Close the HTTP client when done."""
        if hasattr(self, "client"):
            self.client.close()
