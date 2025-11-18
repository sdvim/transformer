from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from transformer.core.static_scraper import StaticScraper
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class GoodreadsScraper(StaticScraper):
    """Goodreads-specific scraper for book shelves."""

    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape Goodreads shelf (public data only)."""
        logger.info("scraping_goodreads", url=url)

        response = self.client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        books = []

        # Find book items
        book_rows = soup.select("tr.bookalike")

        for row in book_rows:
            title_elem = row.select_one(".title a")
            author_elem = row.select_one(".author a")
            rating_elem = row.select_one(".rating")

            if title_elem:
                books.append(
                    {
                        "title": title_elem.get_text(strip=True),
                        "author": author_elem.get_text(strip=True) if author_elem else "",
                        "rating": rating_elem.get_text(strip=True) if rating_elem else "",
                        "url": f"https://goodreads.com{title_elem['href']}",
                    }
                )

        logger.info("goodreads_scrape_complete", books=len(books))
        return books
