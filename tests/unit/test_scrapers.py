from unittest.mock import Mock, patch

import pytest

from transformer.core.static_scraper import StaticScraper
from transformer.scrapers.goodreads import GoodreadsScraper


@pytest.fixture
def mock_response():
    """Mock HTTP response."""
    mock = Mock()
    mock.text = """
    <tr class="bookalike">
        <td class="title"><a href="/book/1">Book Title</a></td>
        <td class="author"><a>Author Name</a></td>
        <td class="rating">4.5</td>
    </tr>
    """
    mock.status_code = 200
    mock.raise_for_status = Mock()
    return mock


def test_goodreads_scraper(mock_response):
    """Test Goodreads scraper."""
    with patch("httpx.Client.get", return_value=mock_response):
        scraper = GoodreadsScraper()
        results = scraper.scrape("https://goodreads.com/shelf/test")

        assert len(results) == 1
        assert results[0]["title"] == "Book Title"
        assert results[0]["author"] == "Author Name"
