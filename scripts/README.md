# Analysis Scripts

This directory contains various analysis scripts for working with Last.fm and YouTube data.

## Last.fm Scripts

### `genre_analysis.py`
Analyze your Last.fm listening data by genre/tags.

```bash
# List all genres in your library
poetry run python scripts/genre_analysis.py list --top 20 --limit 100

# Analyze a specific genre
poetry run python scripts/genre_analysis.py analyze "hip-hop" --top 15
poetry run python scripts/genre_analysis.py analyze "video game music" --top 10

# Compare multiple genres
poetry run python scripts/genre_analysis.py compare "rock" "jazz" "electronic" --top 10
```

**Requirements**: Last.fm API credentials in `.env`

### `analyze_vgm.py`
Find your top video game music artists using Last.fm tags.

```bash
poetry run python scripts/analyze_vgm.py
```

**Requirements**: Last.fm API credentials in `.env`

## YouTube Scripts

### `test_youtube_api.py`
Test and demonstrate YouTube API functionality.

```bash
poetry run python scripts/test_youtube_api.py
```

**Features**:
- Test URL parsing (playlist and video ID extraction)
- Fetch playlist items with metadata
- Get detailed video information
- Format durations and view counts

**Requirements**: YouTube API key in `.env`

## Setup

### Last.fm API
1. Create an API account at https://www.last.fm/api/account/create
2. Add to `.env`:
   ```
   LASTFM_USER=your_username
   LASTFM_API_KEY=your_api_key
   LASTFM_SHARED_SECRET=your_shared_secret
   ```

### YouTube API
1. Get an API key at https://console.cloud.google.com/apis/credentials
2. Enable YouTube Data API v3 for your project
3. Add to `.env`:
   ```
   YOUTUBE_API_KEY=your_api_key
   ```

## Usage in Code

All scripts can also be imported and used programmatically:

```python
# Last.fm genre analysis
from transformer.utils.genre_analyzer import GenreAnalyzer

analyzer = GenreAnalyzer()
hip_hop_artists = analyzer.analyze_top_artists_by_genre("hip-hop", limit=100, top_n=10)
all_genres = analyzer.get_genre_breakdown(artist_limit=100)

# YouTube API
from transformer.scrapers.youtube_api import YouTubeAPI

api = YouTubeAPI()
playlist = api.get_playlist_items("PLxxxxxxxxxxx", max_results=50)
video = api.get_video_info("dQw4w9WgXcQ")
```

## Notes

- All scripts use retry logic with exponential backoff for API calls
- Structured logging is enabled for debugging
- Tests can be run with: `poetry run pytest tests/unit/`
