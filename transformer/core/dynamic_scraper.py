from typing import Any, Dict, List, Optional

from playwright.sync_api import Browser, Page, sync_playwright

from transformer.config import settings
from transformer.core.scraper_base import BaseScraper
from transformer.utils.errors import ClientError, TransientError
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class DynamicScraper(BaseScraper):
    """Scraper for dynamic content using Playwright."""

    def requires_javascript(self) -> bool:
        return True

    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape dynamic content with JavaScript execution."""
        logger.info("scraping_dynamic_content", url=url, selector=selector)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=settings.headless_browser)
            page = browser.new_page()

            try:
                response = page.goto(url, timeout=settings.browser_timeout_ms)

                if response.status in (429, 503):
                    raise TransientError(f"Rate limited: {response.status}")
                if response.status >= 400:
                    raise ClientError(f"HTTP {response.status}")

                # Wait for content to load
                page.wait_for_load_state("networkidle")

                if selector:
                    elements = page.query_selector_all(selector)
                else:
                    elements = [page.query_selector("body")]

                results = []
                for elem in elements:
                    if elem:
                        results.append(
                            {
                                "text": elem.inner_text(),
                                "html": elem.inner_html(),
                                "attrs": elem.get_attribute("class"),  # Example attr
                            }
                        )

                logger.info("scraping_complete", url=url, items_found=len(results))
                return results

            finally:
                browser.close()
