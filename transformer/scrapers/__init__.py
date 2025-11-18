from typing import Optional
from urllib.parse import urlparse

from transformer.core.scraper_base import BaseScraper
from transformer.scrapers.goodreads import GoodreadsScraper
from transformer.scrapers.lastfm import LastFMScraper
from transformer.scrapers.spotify import SpotifyScraper
from transformer.scrapers.wanderlog import WanderlogScraper
from transformer.scrapers.youtube import YouTubeScraper

SITE_SCRAPERS = {
    "youtube.com": YouTubeScraper,
    "youtu.be": YouTubeScraper,
    "spotify.com": SpotifyScraper,
    "goodreads.com": GoodreadsScraper,
    "last.fm": LastFMScraper,
    "lastfm.com": LastFMScraper,
    "wanderlog.com": WanderlogScraper,
}


def get_site_scraper(url: str) -> Optional[BaseScraper]:
    """Get site-specific scraper if available."""
    domain = urlparse(url).netloc.replace("www.", "")

    for site, scraper_class in SITE_SCRAPERS.items():
        if site in domain:
            return scraper_class()

    return None
