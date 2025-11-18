from urllib.parse import urlparse

from transformer.core.dynamic_scraper import DynamicScraper
from transformer.core.scraper_base import BaseScraper
from transformer.core.static_scraper import StaticScraper

# Sites that require JavaScript
DYNAMIC_SITES = {"youtube.com", "open.spotify.com", "wanderlog.com"}


class ScraperFactory:
    """Factory for selecting appropriate scraper."""

    @staticmethod
    def get_scraper(url: str, force_dynamic: bool = False) -> BaseScraper:
        """
        Select scraper based on URL and requirements.

        Args:
            url: URL to scrape
            force_dynamic: Force use of dynamic scraper

        Returns:
            Appropriate scraper instance
        """
        domain = urlparse(url).netloc

        if force_dynamic or any(site in domain for site in DYNAMIC_SITES):
            return DynamicScraper()
        return StaticScraper()
