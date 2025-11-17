# Transformer

A CLI tool that transforms webpages into arbitrary file types by scraping structured data and exporting it in various formats.

## Product Requirements Document (PRD)

### Overview

Transformer is a command-line utility that extracts structured data from web pages and converts it into various file formats. It supports both generic web scraping with CSS/XPath selectors and specialized scrapers for popular websites.

### Use Cases

1. **Wanderlog Itinerary → Calendar Events**
   - Input: Wanderlog trip URL
   - Extract: Event items with dates, locations, activities
   - Output: Google Calendar events (iCalendar format), event links

2. **YouTube Playlist → CSV**
   - Input: YouTube playlist URL
   - Extract: Video titles, channels, durations, view counts
   - Output: CSV file with song/video metadata

3. **Spotify Playlist → JSON**
   - Input: Spotify playlist URL (public)
   - Extract: Track names, artists, albums, durations
   - Output: JSON list of songs

4. **Goodreads Want to Read → Markdown TODO**
   - Input: Goodreads user's "want to read" shelf URL
   - Extract: Book titles, authors, ratings
   - Output: Markdown-formatted reading list with checkboxes

5. **Last.fm Profile → SQLite Database**
   - Input: Last.fm user profile URL
   - Extract: Top artists with play counts, tags
   - Output: SQLite database with artist information

### Usage

```bash
# Generic scraping with CSS selector
transform [url] --selector [css_selector] --output [filename.ext]

# Site-specific commands (auto-detected from URL)
transform [url] --output [filename.ext]

# Examples
transform https://wanderlog.com/trip/xyz --output trip.ics
transform https://youtube.com/playlist?list=xyz --output playlist.csv
transform https://open.spotify.com/playlist/xyz --output playlist.json
transform https://goodreads.com/review/list/123?shelf=to-read --output books.md
transform https://last.fm/user/username --output artists.db
```

## Technology Stack

### Language: Python 3.11+

**Rationale:**
- **Best scraping ecosystem**: Mature, battle-tested libraries (Playwright, BeautifulSoup4, Scrapy)
- **Rich file format support**: Native and third-party libraries for all required formats
- **Testing maturity**: Excellent testing infrastructure (pytest, VCR.py) specifically designed for web scraping
- **Reliability over speed**: Python's mature error handling aligns with project priorities
- **Rapid development**: Quickest path to working prototype for multi-agent development

**Trade-offs:**
- Distribution requires dependency management (vs Go's single binary)
- Slower runtime (acceptable given <1000 items assumption)
- Less portable than compiled languages

### Core Libraries

| Purpose | Library | Justification |
|---------|---------|---------------|
| CLI Framework | Typer | Type-hint based, minimal boilerplate, auto-generated help |
| Dynamic Scraping | Playwright | Handles JavaScript-heavy sites, auto-waits, modern API |
| Static Scraping | BeautifulSoup4 | Fast, easy HTML/XML parsing for simple sites |
| HTTP Client | httpx | Modern, async support, HTTP/2, better retry mechanisms |
| Retry Logic | tenacity | Sophisticated retry/backoff with configurable strategies |
| Testing | pytest | Industry standard with fixtures and parametrization |
| HTTP Mocking | VCR.py | Records/replays HTTP interactions for reliable tests |
| Logging | structlog | Structured logging with JSON output |
| Configuration | pydantic-settings | Type-safe config with environment variable support |
| CSV Export | csv (stdlib) | Native Python CSV handling |
| JSON Export | json (stdlib) | Native Python JSON handling |
| SQLite Export | sqlite3 (stdlib) | Native Python SQLite support |
| iCalendar Export | icalendar | RFC 5545 compliant calendar format |
| Markdown Export | String formatting | Simple text-based format |

## Architecture

### Design Principles

1. **Modularity**: Separate concerns (scraping, extraction, export)
2. **Strategy Pattern**: Pluggable scrapers for different site types
3. **Testability**: All components mockable and testable in isolation
4. **Reliability**: Retry logic, error handling, graceful degradation
5. **Extensibility**: Easy to add new sites and export formats

### Project Structure

```
transformer/
├── pyproject.toml              # Poetry dependencies and metadata
├── README.md                   # This file
├── .gitignore
├── .env.example                # Example environment variables
│
├── transformer/
│   ├── __init__.py
│   ├── __main__.py             # Entry point for `python -m transformer`
│   ├── cli.py                  # Typer CLI definitions
│   ├── config.py               # Configuration management (pydantic-settings)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scraper_base.py     # Abstract base scraper interface
│   │   ├── static_scraper.py   # BeautifulSoup implementation
│   │   ├── dynamic_scraper.py  # Playwright implementation
│   │   └── factory.py          # Scraper factory (auto-detection)
│   │
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── selector.py         # CSS/XPath selector engine
│   │   └── transforms.py       # Data transformation utilities
│   │
│   ├── scrapers/                # Site-specific scrapers
│   │   ├── __init__.py
│   │   ├── youtube.py          # YouTube scraper
│   │   ├── spotify.py          # Spotify scraper
│   │   ├── goodreads.py        # Goodreads scraper
│   │   ├── lastfm.py           # Last.fm scraper
│   │   └── wanderlog.py        # Wanderlog scraper
│   │
│   ├── exporters/               # Output format generators
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract base exporter
│   │   ├── csv_exporter.py
│   │   ├── json_exporter.py
│   │   ├── sqlite_exporter.py
│   │   ├── ical_exporter.py
│   │   └── markdown_exporter.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── retry.py            # Retry/backoff decorators
│       ├── logging.py          # Structured logging setup
│       └── errors.py           # Custom exceptions
│
└── tests/
    ├── __init__.py
    ├── conftest.py             # Pytest configuration and fixtures
    │
    ├── fixtures/               # VCR cassettes and HTML fixtures
    │   ├── vcr_cassettes/      # Recorded HTTP interactions
    │   ├── html/               # Sample HTML from each site
    │   └── expected/           # Expected output files
    │
    ├── unit/                   # Unit tests
    │   ├── test_scrapers.py
    │   ├── test_exporters.py
    │   └── test_extractors.py
    │
    └── integration/            # Integration tests
        └── test_cli.py
```

### Core Interfaces

#### Base Scraper

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

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
```

#### Base Exporter

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path

class BaseExporter(ABC):
    """Abstract base class for all exporters."""

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Returns True if this exporter can handle the given file extension."""
        pass

    @abstractmethod
    def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
        """
        Export data to file.

        Args:
            data: List of dictionaries to export
            output_path: Destination file path

        Raises:
            ExportError: If export fails
        """
        pass
```

## Implementation Guide for Agents

This section provides a step-by-step breakdown for implementing the transformer tool using multiple agents. Each agent task is designed to be completed independently with clear inputs and outputs.

### Agent 1: Project Scaffolding & Configuration

**Objective**: Set up the Python project structure with all necessary dependencies.

**Tasks**:
1. Initialize Python project with Poetry
2. Create `pyproject.toml` with dependencies:
   ```toml
   [tool.poetry]
   name = "transformer"
   version = "0.1.0"
   description = "CLI tool that transforms webpages into arbitrary file types"
   authors = ["Your Name <email@example.com>"]

   [tool.poetry.dependencies]
   python = "^3.11"
   typer = "^0.9.0"
   playwright = "^1.40.0"
   beautifulsoup4 = "^4.12.0"
   httpx = "^0.25.0"
   tenacity = "^8.2.0"
   pydantic-settings = "^2.1.0"
   structlog = "^23.2.0"
   icalendar = "^5.0.0"
   lxml = "^4.9.0"

   [tool.poetry.dev-dependencies]
   pytest = "^7.4.0"
   pytest-asyncio = "^0.21.0"
   pytest-recording = "^0.13.0"
   vcrpy = "^5.1.0"
   black = "^23.12.0"
   isort = "^5.13.0"
   mypy = "^1.7.0"

   [tool.poetry.scripts]
   transform = "transformer.cli:app"
   ```

3. Create directory structure (as shown in Architecture section)
4. Create `.gitignore` with Python/IDE entries
5. Create `.env.example` with configuration variables:
   ```
   # Rate limiting
   SCRAPE_REQUESTS_PER_SECOND=1.0
   SCRAPE_MAX_RETRIES=3

   # Browser settings
   SCRAPE_HEADLESS_BROWSER=true
   SCRAPE_BROWSER_TIMEOUT_MS=30000

   # Logging
   SCRAPE_LOG_LEVEL=INFO
   ```

6. Initialize `transformer/__init__.py` with version info
7. Run `poetry install` and `playwright install` to set up environment

**Validation**: Run `poetry show` to verify all dependencies installed.

**Output**: Complete project skeleton with dependencies ready.

---

### Agent 2: Configuration & Logging Infrastructure

**Objective**: Implement configuration management and structured logging.

**Tasks**:

1. **Create `transformer/config.py`**:
   ```python
   from pydantic_settings import BaseSettings
   from typing import Optional

   class Settings(BaseSettings):
       """Application configuration."""

       # Rate limiting
       requests_per_second: float = 1.0
       max_retries: int = 3
       retry_backoff_multiplier: float = 1.0

       # Browser settings
       headless_browser: bool = True
       browser_timeout_ms: int = 30000

       # Logging
       log_level: str = "INFO"

       class Config:
           env_file = ".env"
           env_prefix = "SCRAPE_"

   settings = Settings()
   ```

2. **Create `transformer/utils/logging.py`**:
   ```python
   import structlog
   from transformer.config import settings

   def setup_logging():
       """Configure structured logging."""
       structlog.configure(
           processors=[
               structlog.stdlib.filter_by_level,
               structlog.stdlib.add_logger_name,
               structlog.stdlib.add_log_level,
               structlog.stdlib.PositionalArgumentsFormatter(),
               structlog.processors.TimeStamper(fmt="iso"),
               structlog.processors.StackInfoRenderer(),
               structlog.processors.format_exc_info,
               structlog.processors.UnicodeDecoder(),
               structlog.processors.JSONRenderer()
           ],
           wrapper_class=structlog.stdlib.BoundLogger,
           logger_factory=structlog.stdlib.LoggerFactory(),
           cache_logger_on_first_use=True,
       )

   def get_logger(name: str):
       """Get a configured logger."""
       return structlog.get_logger(name)
   ```

3. **Create `transformer/utils/errors.py`**:
   ```python
   class TransformerError(Exception):
       """Base exception for transformer errors."""
       pass

   class ScrapeError(TransformerError):
       """Error during scraping."""
       pass

   class TransientError(ScrapeError):
       """Retryable error (network, rate limit)."""
       pass

   class ClientError(ScrapeError):
       """Non-retryable error (403, 404, invalid selector)."""
       pass

   class ParsingError(ScrapeError):
       """Data extraction error."""
       pass

   class ExportError(TransformerError):
       """Error during export."""
       pass
   ```

4. **Create `transformer/utils/retry.py`**:
   ```python
   from tenacity import (
       retry,
       stop_after_attempt,
       wait_exponential,
       retry_if_exception_type
   )
   from transformer.config import settings
   from transformer.utils.errors import TransientError
   import httpx

   def create_retry_decorator():
       """Create a retry decorator with configured settings."""
       return retry(
           stop=stop_after_attempt(settings.max_retries),
           wait=wait_exponential(
               multiplier=settings.retry_backoff_multiplier,
               min=4,
               max=10
           ),
           retry=retry_if_exception_type((
               TransientError,
               httpx.TimeoutException,
               httpx.ConnectError
           ))
       )
   ```

**Validation**:
- Import config in Python REPL: `from transformer.config import settings`
- Verify logging works: `from transformer.utils.logging import setup_logging, get_logger`

**Output**: Configuration, logging, and error handling infrastructure ready.

---

### Agent 3: Core Scraping Engine

**Objective**: Implement base scraper interface and both static/dynamic scrapers.

**Tasks**:

1. **Create `transformer/core/scraper_base.py`**:
   - Implement `BaseScraper` abstract class (see Core Interfaces section)
   - Add `scrape()` and `requires_javascript()` methods

2. **Create `transformer/core/static_scraper.py`**:
   ```python
   from typing import Dict, List, Any, Optional
   import httpx
   from bs4 import BeautifulSoup
   from transformer.core.scraper_base import BaseScraper
   from transformer.utils.retry import create_retry_decorator
   from transformer.utils.logging import get_logger
   from transformer.utils.errors import ClientError, TransientError

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

           soup = BeautifulSoup(response.text, 'lxml')

           if selector:
               elements = soup.select(selector)
           else:
               elements = [soup]

           results = []
           for elem in elements:
               results.append({
                   'text': elem.get_text(strip=True),
                   'html': str(elem),
                   'attrs': elem.attrs if hasattr(elem, 'attrs') else {}
               })

           logger.info("scraping_complete", url=url, items_found=len(results))
           return results
   ```

3. **Create `transformer/core/dynamic_scraper.py`**:
   ```python
   from typing import Dict, List, Any, Optional
   from playwright.sync_api import sync_playwright, Page, Browser
   from transformer.core.scraper_base import BaseScraper
   from transformer.config import settings
   from transformer.utils.logging import get_logger
   from transformer.utils.errors import ClientError, TransientError

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
                   page.wait_for_load_state('networkidle')

                   if selector:
                       elements = page.query_selector_all(selector)
                   else:
                       elements = [page.query_selector('body')]

                   results = []
                   for elem in elements:
                       if elem:
                           results.append({
                               'text': elem.inner_text(),
                               'html': elem.inner_html(),
                               'attrs': elem.get_attribute('class')  # Example attr
                           })

                   logger.info("scraping_complete", url=url, items_found=len(results))
                   return results

               finally:
                   browser.close()
   ```

4. **Create `transformer/core/factory.py`**:
   ```python
   from transformer.core.scraper_base import BaseScraper
   from transformer.core.static_scraper import StaticScraper
   from transformer.core.dynamic_scraper import DynamicScraper
   from urllib.parse import urlparse

   # Sites that require JavaScript
   DYNAMIC_SITES = {
       'youtube.com',
       'open.spotify.com',
       'wanderlog.com'
   }

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
   ```

**Validation**:
- Test static scraper on simple HTML page
- Test dynamic scraper on JavaScript-heavy site
- Verify factory selects correct scraper

**Output**: Working generic scraping engine for both static and dynamic content.

---

### Agent 4: Export Modules

**Objective**: Implement all export formats (CSV, JSON, SQLite, iCalendar, Markdown).

**Tasks**:

1. **Create `transformer/exporters/base.py`**:
   - Implement `BaseExporter` abstract class (see Core Interfaces section)

2. **Create `transformer/exporters/csv_exporter.py`**:
   ```python
   import csv
   from pathlib import Path
   from typing import List, Dict, Any
   from transformer.exporters.base import BaseExporter
   from transformer.utils.logging import get_logger

   logger = get_logger(__name__)

   class CSVExporter(BaseExporter):
       """Export data to CSV format."""

       def can_handle(self, file_path: Path) -> bool:
           return file_path.suffix.lower() == '.csv'

       def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
           """Export data to CSV file."""
           if not data:
               logger.warning("no_data_to_export")
               return

           # Get all unique keys across all dictionaries
           fieldnames = set()
           for item in data:
               fieldnames.update(item.keys())
           fieldnames = sorted(fieldnames)

           with open(output_path, 'w', newline='', encoding='utf-8') as f:
               writer = csv.DictWriter(f, fieldnames=fieldnames)
               writer.writeheader()
               writer.writerows(data)

           logger.info("csv_export_complete", path=str(output_path), rows=len(data))
   ```

3. **Create `transformer/exporters/json_exporter.py`**:
   ```python
   import json
   from pathlib import Path
   from typing import List, Dict, Any
   from transformer.exporters.base import BaseExporter
   from transformer.utils.logging import get_logger

   logger = get_logger(__name__)

   class JSONExporter(BaseExporter):
       """Export data to JSON format."""

       def can_handle(self, file_path: Path) -> bool:
           return file_path.suffix.lower() == '.json'

       def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
           """Export data to JSON file."""
           with open(output_path, 'w', encoding='utf-8') as f:
               json.dump(data, f, indent=2, ensure_ascii=False)

           logger.info("json_export_complete", path=str(output_path), items=len(data))
   ```

4. **Create `transformer/exporters/sqlite_exporter.py`**:
   ```python
   import sqlite3
   from pathlib import Path
   from typing import List, Dict, Any
   from transformer.exporters.base import BaseExporter
   from transformer.utils.logging import get_logger

   logger = get_logger(__name__)

   class SQLiteExporter(BaseExporter):
       """Export data to SQLite database."""

       def can_handle(self, file_path: Path) -> bool:
           return file_path.suffix.lower() in ('.db', '.sqlite', '.sqlite3')

       def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
           """Export data to SQLite database."""
           if not data:
               return

           conn = sqlite3.connect(output_path)
           cursor = conn.cursor()

           # Create table from first item's keys
           columns = list(data[0].keys())
           column_defs = ', '.join([f'"{col}" TEXT' for col in columns])
           cursor.execute(f'CREATE TABLE IF NOT EXISTS items ({column_defs})')

           # Insert data
           placeholders = ', '.join(['?' for _ in columns])
           for item in data:
               values = [str(item.get(col, '')) for col in columns]
               cursor.execute(f'INSERT INTO items VALUES ({placeholders})', values)

           conn.commit()
           conn.close()

           logger.info("sqlite_export_complete", path=str(output_path), rows=len(data))
   ```

5. **Create `transformer/exporters/ical_exporter.py`**:
   ```python
   from datetime import datetime
   from pathlib import Path
   from typing import List, Dict, Any
   from icalendar import Calendar, Event
   from transformer.exporters.base import BaseExporter
   from transformer.utils.logging import get_logger

   logger = get_logger(__name__)

   class ICalExporter(BaseExporter):
       """Export data to iCalendar format."""

       def can_handle(self, file_path: Path) -> bool:
           return file_path.suffix.lower() in ('.ics', '.ical')

       def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
           """Export data to iCalendar file."""
           cal = Calendar()
           cal.add('prodid', '-//Transformer//transformer//EN')
           cal.add('version', '2.0')

           for item in data:
               event = Event()

               # Required fields
               event.add('summary', item.get('title', item.get('text', 'Event')))

               # Optional fields
               if 'start' in item:
                   event.add('dtstart', self._parse_date(item['start']))
               if 'end' in item:
                   event.add('dtend', self._parse_date(item['end']))
               if 'location' in item:
                   event.add('location', item['location'])
               if 'description' in item:
                   event.add('description', item['description'])

               cal.add_component(event)

           with open(output_path, 'wb') as f:
               f.write(cal.to_ical())

           logger.info("ical_export_complete", path=str(output_path), events=len(data))

       def _parse_date(self, date_str: str) -> datetime:
           """Parse date string to datetime object."""
           # Add more sophisticated date parsing as needed
           try:
               return datetime.fromisoformat(date_str)
           except:
               return datetime.now()
   ```

6. **Create `transformer/exporters/markdown_exporter.py`**:
   ```python
   from pathlib import Path
   from typing import List, Dict, Any
   from transformer.exporters.base import BaseExporter
   from transformer.utils.logging import get_logger

   logger = get_logger(__name__)

   class MarkdownExporter(BaseExporter):
       """Export data to Markdown format."""

       def can_handle(self, file_path: Path) -> bool:
           return file_path.suffix.lower() in ('.md', '.markdown')

       def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
           """Export data to Markdown file."""
           lines = []

           for item in data:
               # Create checkbox list item
               title = item.get('title', item.get('text', 'Item'))
               lines.append(f"- [ ] {title}")

               # Add additional details as nested list
               for key, value in item.items():
                   if key not in ('title', 'text') and value:
                       lines.append(f"  - {key}: {value}")

               lines.append('')  # Blank line between items

           with open(output_path, 'w', encoding='utf-8') as f:
               f.write('\n'.join(lines))

           logger.info("markdown_export_complete", path=str(output_path), items=len(data))
   ```

7. **Create `transformer/exporters/__init__.py`** with exporter registry:
   ```python
   from pathlib import Path
   from typing import List, Dict, Any
   from transformer.exporters.base import BaseExporter
   from transformer.exporters.csv_exporter import CSVExporter
   from transformer.exporters.json_exporter import JSONExporter
   from transformer.exporters.sqlite_exporter import SQLiteExporter
   from transformer.exporters.ical_exporter import ICalExporter
   from transformer.exporters.markdown_exporter import MarkdownExporter
   from transformer.utils.errors import ExportError

   EXPORTERS: List[BaseExporter] = [
       CSVExporter(),
       JSONExporter(),
       SQLiteExporter(),
       ICalExporter(),
       MarkdownExporter()
   ]

   def get_exporter(output_path: Path) -> BaseExporter:
       """Get appropriate exporter for file path."""
       for exporter in EXPORTERS:
           if exporter.can_handle(output_path):
               return exporter
       raise ExportError(f"No exporter found for {output_path.suffix}")
   ```

**Validation**:
- Test each exporter with sample data
- Verify output files are correctly formatted

**Output**: All export formats working correctly.

---

### Agent 5: Site-Specific Scrapers

**Objective**: Implement specialized scrapers for all 5 target sites.

**Important Notes**:
- Authentication is deferred (work with public data only)
- Focus on extracting key fields that work without login
- Use selectors that are stable and meaningful

**Tasks**:

1. **Create `transformer/scrapers/youtube.py`**:
   ```python
   from typing import Dict, List, Any, Optional
   import re
   import json
   from transformer.core.dynamic_scraper import DynamicScraper
   from transformer.utils.logging import get_logger

   logger = get_logger(__name__)

   class YouTubeScraper(DynamicScraper):
       """YouTube-specific scraper for playlists and videos."""

       def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
           """Scrape YouTube playlist or video metadata."""

           # Use parent's dynamic scraping to get page
           with sync_playwright() as p:
               browser = p.chromium.launch(headless=True)
               page = browser.new_page()
               page.goto(url)
               page.wait_for_load_state('networkidle')

               # Extract ytInitialData from page
               html = page.content()
               browser.close()

           # Parse hidden JSON data
           match = re.search(r'var ytInitialData = ({.*?});', html)
           if not match:
               logger.warning("youtube_data_not_found")
               return []

           data = json.loads(match.group(1))

           # Extract video items from playlist
           results = []
           if 'playlist' in url:
               results = self._extract_playlist_videos(data)
           else:
               results = [self._extract_video_metadata(data)]

           logger.info("youtube_scrape_complete", videos=len(results))
           return results

       def _extract_playlist_videos(self, data: dict) -> List[Dict[str, Any]]:
           """Extract video list from playlist data."""
           videos = []
           # Navigate JSON structure to find videos
           # This is site-specific and may need updates
           try:
               contents = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']

               for item in contents:
                   if 'playlistVideoRenderer' in item:
                       video = item['playlistVideoRenderer']
                       videos.append({
                           'title': video.get('title', {}).get('runs', [{}])[0].get('text', ''),
                           'channel': video.get('shortBylineText', {}).get('runs', [{}])[0].get('text', ''),
                           'duration': video.get('lengthText', {}).get('simpleText', ''),
                           'video_id': video.get('videoId', '')
                       })
           except (KeyError, IndexError) as e:
               logger.error("youtube_parse_error", error=str(e))

           return videos

       def _extract_video_metadata(self, data: dict) -> Dict[str, Any]:
           """Extract metadata from single video page."""
           # Similar JSON navigation for single video
           return {
               'title': 'Video Title',  # Extract from data
               'channel': 'Channel Name',
               'views': '1000',
               'date': '2024-01-01'
           }
   ```

2. **Create `transformer/scrapers/spotify.py`**:
   ```python
   from typing import Dict, List, Any, Optional
   from transformer.core.dynamic_scraper import DynamicScraper
   from transformer.utils.logging import get_logger

   logger = get_logger(__name__)

   class SpotifyScraper(DynamicScraper):
       """Spotify-specific scraper for public playlists."""

       def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
           """Scrape public Spotify playlist."""
           logger.info("scraping_spotify", url=url)

           # Spotify embeds are easier to scrape than main site
           embed_url = url.replace('open.spotify.com', 'open.spotify.com/embed')

           with sync_playwright() as p:
               browser = p.chromium.launch(headless=True)
               page = browser.new_page()
               page.goto(embed_url)
               page.wait_for_selector('[data-testid="track-row"]', timeout=10000)

               tracks = []
               track_elements = page.query_selector_all('[data-testid="track-row"]')

               for elem in track_elements:
                   title_elem = elem.query_selector('[data-testid="track-title"]')
                   artist_elem = elem.query_selector('[data-testid="track-artist"]')

                   if title_elem and artist_elem:
                       tracks.append({
                           'title': title_elem.inner_text(),
                           'artist': artist_elem.inner_text(),
                           'type': 'track'
                       })

               browser.close()

           logger.info("spotify_scrape_complete", tracks=len(tracks))
           return tracks
   ```

3. **Create `transformer/scrapers/goodreads.py`**:
   ```python
   from typing import Dict, List, Any, Optional
   from transformer.core.static_scraper import StaticScraper
   from bs4 import BeautifulSoup
   import httpx
   from transformer.utils.logging import get_logger

   logger = get_logger(__name__)

   class GoodreadsScraper(StaticScraper):
       """Goodreads-specific scraper for book shelves."""

       def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
           """Scrape Goodreads shelf (public data only)."""
           logger.info("scraping_goodreads", url=url)

           response = self.client.get(url)
           response.raise_for_status()

           soup = BeautifulSoup(response.text, 'lxml')
           books = []

           # Find book items
           book_rows = soup.select('tr.bookalike')

           for row in book_rows:
               title_elem = row.select_one('.title a')
               author_elem = row.select_one('.author a')
               rating_elem = row.select_one('.rating')

               if title_elem:
                   books.append({
                       'title': title_elem.get_text(strip=True),
                       'author': author_elem.get_text(strip=True) if author_elem else '',
                       'rating': rating_elem.get_text(strip=True) if rating_elem else '',
                       'url': f"https://goodreads.com{title_elem['href']}"
                   })

           logger.info("goodreads_scrape_complete", books=len(books))
           return books
   ```

4. **Create `transformer/scrapers/lastfm.py`**:
   ```python
   from typing import Dict, List, Any, Optional
   from transformer.core.static_scraper import StaticScraper
   from bs4 import BeautifulSoup
   from transformer.utils.logging import get_logger

   logger = get_logger(__name__)

   class LastFMScraper(StaticScraper):
       """Last.fm-specific scraper for user profiles."""

       def scrape(self, url: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
           """Scrape Last.fm user's top artists."""
           logger.info("scraping_lastfm", url=url)

           # Ensure we're on the top artists page
           if not url.endswith('/library/artists'):
               url = url.rstrip('/') + '/library/artists'

           response = self.client.get(url)
           response.raise_for_status()

           soup = BeautifulSoup(response.text, 'lxml')
           artists = []

           # Find artist items
           artist_items = soup.select('.chartlist-row')

           for item in artist_items:
               name_elem = item.select_one('.chartlist-name a')
               playcount_elem = item.select_one('.chartlist-count-bar-value')

               if name_elem:
                   artists.append({
                       'artist': name_elem.get_text(strip=True),
                       'playcount': playcount_elem.get_text(strip=True) if playcount_elem else '0',
                       'url': f"https://last.fm{name_elem['href']}"
                   })

           logger.info("lastfm_scrape_complete", artists=len(artists))
           return artists
   ```

5. **Create `transformer/scrapers/wanderlog.py`**:
   ```python
   from typing import Dict, List, Any, Optional
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
               page.wait_for_load_state('networkidle')

               events = []

               # Wait for trip content to load
               try:
                   page.wait_for_selector('.trip-day', timeout=5000)

                   days = page.query_selector_all('.trip-day')
                   for day in days:
                       date_elem = day.query_selector('.day-date')
                       activities = day.query_selector_all('.activity-item')

                       for activity in activities:
                           name_elem = activity.query_selector('.activity-name')
                           location_elem = activity.query_selector('.activity-location')

                           if name_elem:
                               events.append({
                                   'title': name_elem.inner_text(),
                                   'location': location_elem.inner_text() if location_elem else '',
                                   'date': date_elem.inner_text() if date_elem else '',
                                   'type': 'activity'
                               })
               except Exception as e:
                   logger.warning("wanderlog_parse_error", error=str(e))

               browser.close()

           logger.info("wanderlog_scrape_complete", events=len(events))
           return events
   ```

6. **Create `transformer/scrapers/__init__.py`** with site detection:
   ```python
   from urllib.parse import urlparse
   from typing import Optional
   from transformer.core.scraper_base import BaseScraper
   from transformer.scrapers.youtube import YouTubeScraper
   from transformer.scrapers.spotify import SpotifyScraper
   from transformer.scrapers.goodreads import GoodreadsScraper
   from transformer.scrapers.lastfm import LastFMScraper
   from transformer.scrapers.wanderlog import WanderlogScraper

   SITE_SCRAPERS = {
       'youtube.com': YouTubeScraper,
       'youtu.be': YouTubeScraper,
       'spotify.com': SpotifyScraper,
       'goodreads.com': GoodreadsScraper,
       'last.fm': LastFMScraper,
       'lastfm.com': LastFMScraper,
       'wanderlog.com': WanderlogScraper,
   }

   def get_site_scraper(url: str) -> Optional[BaseScraper]:
       """Get site-specific scraper if available."""
       domain = urlparse(url).netloc.replace('www.', '')

       for site, scraper_class in SITE_SCRAPERS.items():
           if site in domain:
               return scraper_class()

       return None
   ```

**Validation**:
- Test each scraper with sample URLs
- Verify data extraction produces reasonable results
- Note: Selectors may need adjustment if sites have changed

**Output**: All 5 site-specific scrapers working with public data.

---

### Agent 6: CLI Implementation

**Objective**: Build the Typer-based command-line interface.

**Tasks**:

1. **Create `transformer/cli.py`**:
   ```python
   from pathlib import Path
   from typing import Optional
   import typer
   from transformer.core.factory import ScraperFactory
   from transformer.scrapers import get_site_scraper
   from transformer.exporters import get_exporter
   from transformer.utils.logging import setup_logging, get_logger
   from transformer.utils.errors import TransformerError

   setup_logging()
   logger = get_logger(__name__)

   app = typer.Typer(
       name="transform",
       help="Transform webpages into arbitrary file types",
       add_completion=False
   )

   @app.command()
   def transform(
       url: str = typer.Argument(..., help="URL to scrape"),
       output: Path = typer.Option(..., "--output", "-o", help="Output file path"),
       selector: Optional[str] = typer.Option(None, "--selector", "-s", help="CSS selector for elements"),
       dynamic: bool = typer.Option(False, "--dynamic", "-d", help="Force dynamic scraping (JavaScript)"),
       verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging")
   ):
       """
       Transform webpage data into various file formats.

       Examples:

         transform https://youtube.com/playlist?list=xyz -o playlist.csv

         transform https://goodreads.com/shelf/to-read -o books.md

         transform https://example.com -s "div.content" -o data.json
       """
       try:
           # Try site-specific scraper first
           scraper = get_site_scraper(url)
           if scraper:
               logger.info("using_site_specific_scraper", url=url)
           else:
               # Fall back to generic scraper
               scraper = ScraperFactory.get_scraper(url, force_dynamic=dynamic)
               logger.info("using_generic_scraper", url=url, dynamic=dynamic)

           # Scrape data
           typer.echo(f"Scraping {url}...")
           data = scraper.scrape(url, selector)

           if not data:
               typer.echo("No data extracted", err=True)
               raise typer.Exit(1)

           typer.echo(f"Extracted {len(data)} items")

           # Export data
           exporter = get_exporter(output)
           typer.echo(f"Exporting to {output}...")
           exporter.export(data, output)

           typer.echo(f"✓ Success! Saved to {output}")

       except TransformerError as e:
           logger.error("transform_error", error=str(e))
           typer.echo(f"Error: {e}", err=True)
           raise typer.Exit(1)
       except Exception as e:
           logger.exception("unexpected_error")
           typer.echo(f"Unexpected error: {e}", err=True)
           raise typer.Exit(1)

   @app.command()
   def version():
       """Show version information."""
       typer.echo("transformer 0.1.0")

   if __name__ == "__main__":
       app()
   ```

2. **Create `transformer/__main__.py`**:
   ```python
   from transformer.cli import app

   if __name__ == "__main__":
       app()
   ```

3. **Update `transformer/__init__.py`**:
   ```python
   """Transformer - CLI tool for transforming webpages into file formats."""

   __version__ = "0.1.0"
   ```

**Validation**:
- Run `poetry run transform --help` to see help text
- Test with sample URL and output file
- Verify error handling works correctly

**Output**: Working CLI that ties all components together.

---

### Agent 7: Testing Infrastructure

**Objective**: Implement comprehensive test suite with pytest and VCR.py.

**Tasks**:

1. **Create `tests/conftest.py`**:
   ```python
   import pytest
   from pathlib import Path

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
           {'title': 'Item 1', 'description': 'Description 1'},
           {'title': 'Item 2', 'description': 'Description 2'}
       ]
   ```

2. **Create `tests/unit/test_exporters.py`**:
   ```python
   import pytest
   import json
   import csv
   import sqlite3
   from pathlib import Path
   from transformer.exporters import (
       CSVExporter,
       JSONExporter,
       SQLiteExporter,
       MarkdownExporter,
       ICalExporter
   )

   def test_csv_exporter(tmp_path, sample_data):
       """Test CSV export."""
       output = tmp_path / "test.csv"
       exporter = CSVExporter()

       assert exporter.can_handle(output)
       exporter.export(sample_data, output)

       # Verify CSV content
       with open(output) as f:
           reader = csv.DictReader(f)
           rows = list(reader)
           assert len(rows) == 2
           assert rows[0]['title'] == 'Item 1'

   def test_json_exporter(tmp_path, sample_data):
       """Test JSON export."""
       output = tmp_path / "test.json"
       exporter = JSONExporter()

       exporter.export(sample_data, output)

       # Verify JSON content
       with open(output) as f:
           data = json.load(f)
           assert len(data) == 2
           assert data[0]['title'] == 'Item 1'

   def test_sqlite_exporter(tmp_path, sample_data):
       """Test SQLite export."""
       output = tmp_path / "test.db"
       exporter = SQLiteExporter()

       exporter.export(sample_data, output)

       # Verify database content
       conn = sqlite3.connect(output)
       cursor = conn.cursor()
       cursor.execute("SELECT * FROM items")
       rows = cursor.fetchall()
       assert len(rows) == 2
       conn.close()

   def test_markdown_exporter(tmp_path, sample_data):
       """Test Markdown export."""
       output = tmp_path / "test.md"
       exporter = MarkdownExporter()

       exporter.export(sample_data, output)

       # Verify markdown content
       content = output.read_text()
       assert '- [ ] Item 1' in content
       assert '- [ ] Item 2' in content
   ```

3. **Create `tests/unit/test_scrapers.py`**:
   ```python
   import pytest
   from unittest.mock import Mock, patch
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
       with patch('httpx.Client.get', return_value=mock_response):
           scraper = GoodreadsScraper()
           results = scraper.scrape('https://goodreads.com/shelf/test')

           assert len(results) == 1
           assert results[0]['title'] == 'Book Title'
           assert results[0]['author'] == 'Author Name'
   ```

4. **Create `tests/fixtures/vcr_cassettes/` directory** and add `.gitkeep`

5. **Create example VCR test in `tests/integration/test_vcr.py`**:
   ```python
   import pytest
   import vcr
   from transformer.scrapers.lastfm import LastFMScraper

   @pytest.mark.vcr()
   def test_lastfm_with_vcr():
       """
       Test Last.fm scraper with VCR recording.

       First run: Records HTTP interaction
       Subsequent runs: Replays from cassette
       """
       scraper = LastFMScraper()
       results = scraper.scrape('https://www.last.fm/user/example')

       assert len(results) > 0
       assert 'artist' in results[0]
       assert 'playcount' in results[0]

   @pytest.fixture(scope='module')
   def vcr_config():
       """VCR configuration."""
       return {
           'cassette_library_dir': 'tests/fixtures/vcr_cassettes',
           'record_mode': 'once',  # 'once', 'new_episodes', 'none', 'all'
           'match_on': ['uri', 'method'],
       }
   ```

6. **Create `tests/integration/test_cli.py`**:
   ```python
   import pytest
   from typer.testing import CliRunner
   from transformer.cli import app
   from pathlib import Path

   runner = CliRunner()

   def test_cli_help():
       """Test CLI help command."""
       result = runner.invoke(app, ["--help"])
       assert result.exit_code == 0
       assert "Transform webpages" in result.output

   def test_cli_version():
       """Test version command."""
       result = runner.invoke(app, ["version"])
       assert result.exit_code == 0
       assert "0.1.0" in result.output
   ```

7. **Update `pyproject.toml`** with pytest configuration:
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = ["test_*.py"]
   python_classes = ["Test*"]
   python_functions = ["test_*"]
   addopts = "-v --tb=short"
   ```

**Validation**:
- Run `poetry run pytest` to execute all tests
- Verify unit tests pass
- Check test coverage

**Output**: Comprehensive test suite with mocking and VCR support.

---

### Agent 8: Documentation & Final Integration

**Objective**: Create usage documentation, add examples, and perform final integration testing.

**Tasks**:

1. **Create `USAGE.md`** with detailed examples:
   ```markdown
   # Usage Guide

   ## Installation

   \```bash
   git clone https://github.com/yourusername/transformer.git
   cd transformer
   poetry install
   playwright install chromium
   \```

   ## Basic Usage

   ### Generic Scraping

   \```bash
   # Scrape with CSS selector
   poetry run transform https://example.com \
       --selector "div.product" \
       --output products.json

   # Force dynamic scraping for JavaScript sites
   poetry run transform https://spa-site.com \
       --dynamic \
       --output data.csv
   \```

   ### Site-Specific Examples

   [Include examples for each of the 5 sites]
   \```

2. **Create example fixture data** in `tests/fixtures/html/`:
   - `youtube_playlist.html`
   - `spotify_playlist.html`
   - `goodreads_shelf.html`
   - `lastfm_profile.html`
   - `wanderlog_trip.html`

3. **Add integration test** that runs full pipeline:
   ```python
   def test_full_pipeline(tmp_path):
       """Test complete scrape-to-export pipeline."""
       # Use fixtures or VCR cassettes
       # Test each site-specific scraper
       # Verify output files
   ```

4. **Create `.github/workflows/test.yml`** for CI:
   ```yaml
   name: Tests

   on: [push, pull_request]

   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         - name: Install dependencies
           run: |
             pip install poetry
             poetry install
             poetry run playwright install chromium
         - name: Run tests
           run: poetry run pytest
   ```

5. **Update main README.md** with:
   - Installation instructions
   - Quick start guide
   - Links to USAGE.md
   - Contributing guidelines
   - Known limitations

6. **Create `CONTRIBUTING.md`**:
   - How to add new scrapers
   - How to add new export formats
   - Testing guidelines
   - Code style (black, isort, mypy)

7. **Run final validation**:
   ```bash
   # Format code
   poetry run black transformer tests
   poetry run isort transformer tests

   # Type checking
   poetry run mypy transformer

   # Run all tests
   poetry run pytest

   # Test CLI
   poetry run transform --help
   ```

**Validation**:
- All tests pass
- Documentation is complete and accurate
- CLI works end-to-end for at least one example per site

**Output**: Production-ready tool with complete documentation.

---

## Testing Strategy

### Test Pyramid

1. **Unit Tests** (60%):
   - Test each module in isolation
   - Mock external dependencies
   - Fast execution (<1s)

2. **Integration Tests** (30%):
   - Test component interactions
   - Use VCR.py for HTTP recording
   - Moderate execution time

3. **End-to-End Tests** (10%):
   - Test full CLI workflows
   - Use fixtures or real sites (marked `@pytest.mark.slow`)
   - Run in CI only

### VCR.py Workflow

1. **First run** (record mode):
   ```bash
   pytest tests/integration/test_youtube.py --vcr-record=once
   ```
   - Makes real HTTP requests
   - Saves responses to `tests/fixtures/vcr_cassettes/test_youtube.yaml`

2. **Subsequent runs** (playback mode):
   - Reads from cassette file
   - No network calls
   - Fast and deterministic

3. **Update cassettes** when sites change:
   ```bash
   pytest --vcr-record=new_episodes
   ```

### Mock Data Strategy

**For each site, create**:
- `fixtures/html/{site}_sample.html` - Representative HTML
- `fixtures/expected/{site}_output.{csv,json,etc}` - Expected parsed output

**Example test**:
```python
def test_youtube_parser(fixtures_dir):
    with open(fixtures_dir / 'html/youtube_playlist.html') as f:
        html = f.read()

    # Parse HTML
    scraper = YouTubeScraper()
    result = scraper._extract_playlist_videos(html)

    # Load expected output
    with open(fixtures_dir / 'expected/youtube_playlist.json') as f:
        expected = json.load(f)

    assert result == expected
```

## Best Practices

### 1. Rate Limiting

Always respect site rate limits:
```python
from transformer.config import settings
import time

class RateLimitedScraper:
    def __init__(self):
        self.last_request = 0

    def scrape(self, url):
        # Enforce rate limit
        elapsed = time.time() - self.last_request
        wait_time = (1.0 / settings.requests_per_second) - elapsed
        if wait_time > 0:
            time.sleep(wait_time)

        # Make request
        result = self._do_scrape(url)
        self.last_request = time.time()
        return result
```

### 2. Error Handling

Use specific exceptions and retry transient errors:
```python
from transformer.utils.retry import create_retry_decorator
from transformer.utils.errors import TransientError, ClientError

@create_retry_decorator()
def fetch_page(url):
    try:
        response = httpx.get(url)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (429, 503):
            raise TransientError("Rate limited") from e
        raise ClientError(f"HTTP {e.response.status_code}") from e
    return response
```

### 3. Logging

Use structured logging for debugging:
```python
from transformer.utils.logging import get_logger

logger = get_logger(__name__)

def scrape_item(item_id):
    logger.info(
        "scraping_item",
        item_id=item_id,
        timestamp=datetime.now().isoformat()
    )

    try:
        # Scraping logic
        result = do_scrape(item_id)
        logger.info("scrape_success", item_id=item_id, size=len(result))
        return result
    except Exception as e:
        logger.error("scrape_failed", item_id=item_id, error=str(e))
        raise
```

### 4. Selector Maintenance

Keep selectors organized and documented:
```python
class YouTubeSelectors:
    """CSS selectors for YouTube elements."""

    VIDEO_TITLE = "h1.title.ytd-video-primary-info-renderer"
    CHANNEL_NAME = "ytd-channel-name a"
    VIEW_COUNT = "span.view-count"

    # Document when selectors were last verified
    LAST_VERIFIED = "2024-01-15"
```

## Known Limitations

### MVP Scope (No Authentication)

- **YouTube**: Only public videos/playlists
- **Spotify**: Only embed-based public playlists
- **Goodreads**: Only publicly visible shelves
- **Last.fm**: Only public profile data
- **Wanderlog**: Only public trips

Authentication support can be added in Phase 2.

### Site Stability

Web scraping is inherently fragile. Sites may:
- Change HTML structure (breaking selectors)
- Implement anti-bot measures
- Rate limit requests
- Change data format

**Mitigation**:
- Use site-specific scrapers that can be updated independently
- Implement robust error handling
- Log detailed errors for debugging
- Consider API alternatives where available

### Performance

- Playwright-based scraping is slow (~2-5s per page)
- Not suitable for large-scale scraping (>10k items)
- No built-in concurrency (can be added later)

## Future Enhancements

### Phase 2: Authentication
- OAuth flow support (Spotify, YouTube)
- Session management (Goodreads, Wanderlog)
- Credential storage with keyring

### Phase 3: Advanced Features
- Pagination support
- Concurrent scraping
- Proxy rotation
- Incremental updates
- Data validation with JSON Schema

### Phase 4: API Integration
- Prefer APIs over scraping where available
- Fallback to scraping when API unavailable
- Unified interface for both approaches

## Support & Contributing

### Getting Help

- Check USAGE.md for examples
- Review test files for usage patterns
- Open issue on GitHub for bugs

### Adding New Sites

1. Create scraper in `transformer/scrapers/{site}.py`
2. Inherit from `StaticScraper` or `DynamicScraper`
3. Implement `scrape()` method
4. Add to `SITE_SCRAPERS` dict
5. Create tests with VCR cassettes
6. Document selectors and limitations

### Adding Export Formats

1. Create exporter in `transformer/exporters/{format}_exporter.py`
2. Inherit from `BaseExporter`
3. Implement `can_handle()` and `export()` methods
4. Add to `EXPORTERS` list
5. Create unit tests
6. Update documentation

## License

MIT License - see LICENSE file for details.
