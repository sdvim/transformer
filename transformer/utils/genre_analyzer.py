"""Generic Last.fm genre/tag analysis utilities."""

from typing import Any, Dict, List, Optional, Set

from transformer.scrapers.lastfm_api import LastFMAPI
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class GenreAnalyzer:
    """Analyze Last.fm listening data by genre/tags."""

    def __init__(self, api: Optional[LastFMAPI] = None):
        """
        Initialize GenreAnalyzer.

        Args:
            api: LastFMAPI instance (creates new one if not provided)
        """
        self.api = api or LastFMAPI()

    def get_artist_tags(self, artist: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get tags for a specific artist.

        Args:
            artist: Artist name
            limit: Maximum number of tags to return

        Returns:
            List of tag dictionaries with name and count
        """
        params = {"method": "artist.gettoptags", "artist": artist, "limit": limit}

        data = self.api._make_request(params)
        tags = []

        toptags = data.get("toptags", {})
        tag_list = toptags.get("tag", [])

        for tag in tag_list:
            tags.append({"name": tag.get("name", ""), "count": int(tag.get("count", 0))})

        return tags

    def get_user_top_tags(
        self, username: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get user's top tags based on their listening history.

        Args:
            username: Last.fm username (defaults to configured user)
            limit: Number of tags to return

        Returns:
            List of tag dictionaries with name and count
        """
        user = username or self.api.username
        if not user:
            raise ValueError("Username is required")

        params = {"method": "user.gettoptags", "user": user, "limit": limit}

        data = self.api._make_request(params)
        tags = []

        toptags = data.get("toptags", {})
        tag_list = toptags.get("tag", [])

        for tag in tag_list:
            tags.append({"name": tag.get("name", ""), "count": int(tag.get("count", 0))})

        logger.info("user_top_tags_fetched", tags=len(tags))
        return tags

    def filter_artists_by_tags(
        self,
        artists: List[Dict[str, Any]],
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        threshold: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Filter artists by their tags.

        Args:
            artists: List of artist dictionaries
            include_tags: Tags that should be present (OR logic)
            exclude_tags: Tags that should NOT be present
            threshold: Minimum tag count to consider a tag valid

        Returns:
            Filtered list of artists with tag information
        """
        include_set = set(tag.lower() for tag in (include_tags or []))
        exclude_set = set(tag.lower() for tag in (exclude_tags or []))

        filtered = []

        for artist in artists:
            artist_name = artist.get("artist", "")
            if not artist_name:
                continue

            try:
                # Fetch tags for this artist
                tags = self.get_artist_tags(artist_name, limit=20)
                tag_names = {tag["name"].lower() for tag in tags if tag["count"] >= threshold}

                # Check exclusions first
                if exclude_set and tag_names & exclude_set:
                    continue

                # Check inclusions (if specified)
                if include_set and not (tag_names & include_set):
                    continue

                # Add tag information to artist data
                artist_with_tags = artist.copy()
                artist_with_tags["tags"] = [tag["name"] for tag in tags[:5]]  # Top 5 tags
                filtered.append(artist_with_tags)

            except Exception as e:
                logger.warning("failed_to_fetch_tags", artist=artist_name, error=str(e))
                continue

        logger.info("artists_filtered", original=len(artists), filtered=len(filtered))
        return filtered

    def analyze_top_artists_by_genre(
        self, genre: str, limit: int = 50, top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get user's top artists for a specific genre.

        Args:
            genre: Genre/tag to filter by
            limit: Number of top artists to fetch initially
            top_n: Number of results to return

        Returns:
            List of top artists in the genre with playcount and tags
        """
        logger.info("analyzing_genre", genre=genre)

        # Fetch user's top artists
        artists = self.api.get_top_artists(limit=limit)

        # Filter by genre
        filtered = self.filter_artists_by_tags(artists, include_tags=[genre])

        # Sort by playcount and return top N
        filtered.sort(key=lambda x: int(x.get("playcount", 0)), reverse=True)

        return filtered[:top_n]

    def get_genre_breakdown(
        self, artist_limit: int = 100, tag_threshold: int = 30
    ) -> Dict[str, Any]:
        """
        Get a comprehensive breakdown of genres in user's listening history.

        Args:
            artist_limit: Number of top artists to analyze
            tag_threshold: Minimum tag count to include

        Returns:
            Dictionary with genre statistics and artist counts
        """
        logger.info("analyzing_genre_breakdown", artist_limit=artist_limit)

        # Fetch top artists
        artists = self.api.get_top_artists(limit=artist_limit)

        # Collect all tags with counts
        tag_stats: Dict[str, Dict[str, Any]] = {}

        for artist in artists:
            artist_name = artist.get("artist", "")
            playcount = int(artist.get("playcount", 0))

            try:
                tags = self.get_artist_tags(artist_name, limit=10)

                for tag in tags:
                    tag_name = tag["name"]
                    tag_count = tag["count"]

                    if tag_count < tag_threshold:
                        continue

                    if tag_name not in tag_stats:
                        tag_stats[tag_name] = {
                            "tag": tag_name,
                            "artist_count": 0,
                            "total_plays": 0,
                            "artists": [],
                        }

                    tag_stats[tag_name]["artist_count"] += 1
                    tag_stats[tag_name]["total_plays"] += playcount
                    tag_stats[tag_name]["artists"].append(
                        {"artist": artist_name, "playcount": playcount}
                    )

            except Exception as e:
                logger.warning("failed_to_process_artist", artist=artist_name, error=str(e))
                continue

        # Sort tags by total plays
        sorted_tags = sorted(tag_stats.values(), key=lambda x: x["total_plays"], reverse=True)

        # Limit artists list for each tag
        for tag in sorted_tags:
            tag["artists"] = sorted(tag["artists"], key=lambda x: x["playcount"], reverse=True)[:5]

        logger.info("genre_breakdown_complete", total_genres=len(sorted_tags))

        return {"genres": sorted_tags, "total_artists_analyzed": len(artists)}


def get_genre_stats(genre: str, limit: int = 50, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Quick helper to get top artists for a specific genre.

    Args:
        genre: Genre/tag to analyze
        limit: Number of artists to analyze
        top_n: Number of results to return

    Returns:
        List of top artists in the genre
    """
    analyzer = GenreAnalyzer()
    return analyzer.analyze_top_artists_by_genre(genre, limit=limit, top_n=top_n)


def get_all_genres(artist_limit: int = 100) -> Dict[str, Any]:
    """
    Quick helper to get all genres from user's listening history.

    Args:
        artist_limit: Number of artists to analyze

    Returns:
        Dictionary with genre breakdown
    """
    analyzer = GenreAnalyzer()
    return analyzer.get_genre_breakdown(artist_limit=artist_limit)
