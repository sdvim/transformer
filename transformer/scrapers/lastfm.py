from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from transformer.config import lastfm_settings
from transformer.core.static_scraper import StaticScraper
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class LastFMScraper(StaticScraper):
    """Last.fm-specific scraper for user profiles with API support."""

    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape Last.fm user's top artists.

        Prefers API if credentials are configured, falls back to web scraping.
        """
        logger.info("scraping_lastfm", url=url)

        # Try to use API if credentials are available
        if lastfm_settings.api_key:
            try:
                return self._scrape_with_api(url)
            except Exception as e:
                logger.warning("lastfm_api_failed", error=str(e), fallback="web_scraping")
                # Fall back to web scraping

        # Web scraping fallback
        return self._scrape_with_web(url)

    def _scrape_with_api(self, url: str) -> List[Dict[str, Any]]:
        """Scrape using Last.fm API."""
        from transformer.scrapers.lastfm_api import LastFMAPI

        # Extract username from URL
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) >= 2 and path_parts[0] == "user":
            username = path_parts[1]
        else:
            # Fall back to configured username
            username = lastfm_settings.user

        logger.info("using_lastfm_api", username=username)

        api = LastFMAPI()
        artists = api.get_top_artists(username=username, limit=50)

        logger.info("lastfm_api_complete", artists=len(artists))
        return artists

    def _scrape_with_web(self, url: str) -> List[Dict[str, Any]]:
        """Scrape using web scraping."""
        logger.info("using_web_scraping", url=url)

        # Ensure we're on the top artists page
        if not url.endswith("/library/artists"):
            url = url.rstrip("/") + "/library/artists"

        response = self.client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        artists = []

        # Find artist items
        artist_items = soup.select(".chartlist-row")

        for item in artist_items:
            name_elem = item.select_one(".chartlist-name a")
            playcount_elem = item.select_one(".chartlist-count-bar-value")

            if name_elem:
                artists.append(
                    {
                        "artist": name_elem.get_text(strip=True),
                        "playcount": playcount_elem.get_text(strip=True) if playcount_elem else "0",
                        "url": f"https://last.fm{name_elem['href']}",
                    }
                )

        logger.info("lastfm_scrape_complete", artists=len(artists))
        return artists
