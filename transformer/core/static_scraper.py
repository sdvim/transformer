from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from transformer.core.scraper_base import BaseScraper
from transformer.utils.errors import ClientError, TransientError
from transformer.utils.logging import get_logger
from transformer.utils.retry import create_retry_decorator

logger = get_logger(__name__)
retry = create_retry_decorator()


class StaticScraper(BaseScraper):
    """Scraper for static HTML content using BeautifulSoup."""

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def requires_javascript(self) -> bool:
        return False

    @retry
    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape static HTML content."""
        logger.info("scraping_static_content", url=url, selector=selector)

        try:
            response = self.client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 503):
                raise TransientError(f"Rate limited: {e}")
            raise ClientError(f"HTTP error: {e}")
        except httpx.TimeoutException:
            raise TransientError("Request timeout")

        soup = BeautifulSoup(response.text, "lxml")

        if selector:
            elements = soup.select(selector)
        else:
            elements = [soup]

        results = []
        for elem in elements:
            results.append(
                {
                    "text": elem.get_text(strip=True),
                    "html": str(elem),
                    "attrs": elem.attrs if hasattr(elem, "attrs") else {},
                }
            )

        logger.info("scraping_complete", url=url, items_found=len(results))
        return results
