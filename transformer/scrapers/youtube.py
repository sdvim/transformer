import json
import re
from typing import Any, Dict, List, Optional

from playwright.sync_api import sync_playwright

from transformer.core.dynamic_scraper import DynamicScraper
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class YouTubeScraper(DynamicScraper):
    """YouTube-specific scraper for playlists and videos."""

    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape YouTube playlist or video metadata."""

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
