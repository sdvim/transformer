from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_html():
    """Sample HTML for testing."""
    return """
    <html>
        <body>
            <div class="item">
                <h2>Item 1</h2>
                <p>Description 1</p>
            </div>
            <div class="item">
                <h2>Item 2</h2>
                <p>Description 2</p>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_data():
    """Sample scraped data."""
    return [
        {"title": "Item 1", "description": "Description 1"},
        {"title": "Item 2", "description": "Description 2"},
    ]
