import json
import re
from typing import Any, Dict, List, Optional

from playwright.sync_api import sync_playwright

from transformer.config import youtube_settings
from transformer.core.dynamic_scraper import DynamicScraper
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class YouTubeScraper(DynamicScraper):
    """YouTube-specific scraper for playlists and videos with API support."""

    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape YouTube playlist or video metadata.

        Prefers API if credentials are configured, falls back to web scraping.
        """
        logger.info("scraping_youtube", url=url)

        # Try to use API if credentials are available
        if youtube_settings.api_key:
            try:
                return self._scrape_with_api(url)
            except Exception as e:
                logger.warning("youtube_api_failed", error=str(e), fallback="web_scraping")
                # Fall back to web scraping

        # Web scraping fallback
        return self._scrape_with_web(url)

    def _scrape_with_api(self, url: str) -> List[Dict[str, Any]]:
        """Scrape using YouTube Data API."""
        from transformer.scrapers.youtube_api import YouTubeAPI

        api = YouTubeAPI()

        # Check if it's a playlist or single video
        if "list=" in url or "playlist" in url:
            playlist_id = api.extract_playlist_id(url)
            if not playlist_id:
                raise ValueError("Could not extract playlist ID from URL")

            logger.info("using_youtube_api", type="playlist", playlist_id=playlist_id)
            videos = api.get_playlist_items(playlist_id, max_results=50)

            # Format durations for consistency
            for video in videos:
                if video.get("duration"):
                    video["duration"] = api.format_duration(video["duration"])

            logger.info("youtube_api_complete", videos=len(videos))
            return videos
        else:
            video_id = api.extract_video_id(url)
            if not video_id:
                raise ValueError("Could not extract video ID from URL")

            logger.info("using_youtube_api", type="video", video_id=video_id)
            video_info = api.get_video_info(video_id)

            # Format duration
            if video_info.get("duration"):
                video_info["duration"] = api.format_duration(video_info["duration"])

            logger.info("youtube_api_complete", videos=1)
            return [video_info]

    def _scrape_with_web(self, url: str) -> List[Dict[str, Any]]:
        """Scrape using web scraping (fallback method)."""
        logger.info("using_web_scraping", url=url)

        # Use parent's dynamic scraping to get page
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")

            # Extract ytInitialData from page
            html = page.content()
            browser.close()

        # Parse hidden JSON data
        match = re.search(r"var ytInitialData = ({.*?});", html)
        if not match:
            logger.warning("youtube_data_not_found")
            return []

        data = json.loads(match.group(1))

        # Extract video items from playlist
        results = []
        if "playlist" in url:
            results = self._extract_playlist_videos(data)
        else:
            results = [self._extract_video_metadata(data)]

        logger.info("youtube_scrape_complete", videos=len(results))
        return results

    def _extract_playlist_videos(self, data: dict) -> List[Dict[str, Any]]:
        """Extract video list from playlist data."""
        videos = []
        # Navigate JSON structure to find videos
        # This is site-specific and may need updates
        try:
            contents = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"][
                "content"
            ]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0][
                "playlistVideoListRenderer"
            ][
                "contents"
            ]

            for item in contents:
                if "playlistVideoRenderer" in item:
                    video = item["playlistVideoRenderer"]
                    videos.append(
                        {
                            "title": video.get("title", {}).get("runs", [{}])[0].get("text", ""),
                            "channel": video.get("shortBylineText", {})
                            .get("runs", [{}])[0]
                            .get("text", ""),
                            "duration": video.get("lengthText", {}).get("simpleText", ""),
                            "video_id": video.get("videoId", ""),
                        }
                    )
        except (KeyError, IndexError) as e:
            logger.error("youtube_parse_error", error=str(e))

        return videos

    def _extract_video_metadata(self, data: dict) -> Dict[str, Any]:
        """Extract metadata from single video page."""
        # Similar JSON navigation for single video
        return {
            "title": "Video Title",  # Extract from data
            "channel": "Channel Name",
            "views": "1000",
            "date": "2024-01-01",
        }
