from typing import Any, Dict, List, Optional

from playwright.sync_api import sync_playwright

from transformer.core.dynamic_scraper import DynamicScraper
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class SpotifyScraper(DynamicScraper):
    """Spotify-specific scraper for public playlists."""

    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape public Spotify playlist."""
        logger.info("scraping_spotify", url=url)

        # Spotify embeds are easier to scrape than main site
        embed_url = url.replace("open.spotify.com", "open.spotify.com/embed")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(embed_url)
            page.wait_for_selector('[data-testid="track-row"]', timeout=10000)

            tracks = []
            track_elements = page.query_selector_all('[data-testid="track-row"]')

            for elem in track_elements:
                title_elem = elem.query_selector('[data-testid="track-title"]')
                artist_elem = elem.query_selector('[data-testid="track-artist"]')

                if title_elem and artist_elem:
                    tracks.append(
                        {
                            "title": title_elem.inner_text(),
                            "artist": artist_elem.inner_text(),
                            "type": "track",
                        }
                    )

            browser.close()

        logger.info("spotify_scrape_complete", tracks=len(tracks))
        return tracks
