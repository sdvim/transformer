from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from transformer.core.static_scraper import StaticScraper
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class LastFMScraper(StaticScraper):
    """Last.fm-specific scraper for user profiles."""

    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape Last.fm user's top artists."""
        logger.info("scraping_lastfm", url=url)

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
