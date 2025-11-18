from typing import Any, Dict, List, Optional

from playwright.sync_api import sync_playwright

from transformer.core.dynamic_scraper import DynamicScraper
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class WanderlogScraper(DynamicScraper):
    """Wanderlog-specific scraper for trip itineraries."""

    def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape Wanderlog trip itinerary (public trips only)."""
        logger.info("scraping_wanderlog", url=url)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")

            events = []

            # Wait for trip content to load
            try:
                page.wait_for_selector(".trip-day", timeout=5000)

                days = page.query_selector_all(".trip-day")
                for day in days:
                    date_elem = day.query_selector(".day-date")
                    activities = day.query_selector_all(".activity-item")

                    for activity in activities:
                        name_elem = activity.query_selector(".activity-name")
                        location_elem = activity.query_selector(".activity-location")

                        if name_elem:
                            events.append(
                                {
                                    "title": name_elem.inner_text(),
                                    "location": location_elem.inner_text() if location_elem else "",
                                    "date": date_elem.inner_text() if date_elem else "",
                                    "type": "activity",
                                }
                            )
            except Exception as e:
                logger.warning("wanderlog_parse_error", error=str(e))

            browser.close()

        logger.info("wanderlog_scrape_complete", events=len(events))
        return events
