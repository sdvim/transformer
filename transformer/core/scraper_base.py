from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    @abstractmethod
    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape data from URL.

        Args:
            url: The URL to scrape
            selector: Optional CSS/XPath selector to filter elements

        Returns:
            List of dictionaries containing scraped data

        Raises:
            ScrapeError: If scraping fails
        """
        pass

    @abstractmethod
    def requires_javascript(self) -> bool:
        """Returns True if this scraper needs JavaScript execution."""
        pass
