#!/usr/bin/env python3
"""CLI tool for analyzing Last.fm listening data by genre/tags."""

import argparse

from transformer.utils.genre_analyzer import GenreAnalyzer


def list_all_genres(args):
    """List all genres in user's listening history."""
    print("Analyzing your listening history for genres...")
    print("=" * 70)

    analyzer = GenreAnalyzer()
    result = analyzer.get_genre_breakdown(artist_limit=args.limit)

    genres = result["genres"]
    total_artists = result["total_artists_analyzed"]

    print(f"\nAnalyzed {total_artists} artists")
    print(f"Found {len(genres)} genres/tags\n")
    print("=" * 70)
    print("TOP GENRES BY TOTAL PLAYS")
    print("=" * 70)

    for i, genre in enumerate(genres[: args.top], 1):
        print(f"\n{i}. {genre['tag']}")
        print(f"   Artists: {genre['artist_count']}")
        print(f"   Total plays: {genre['total_plays']:,}")
        print(f"   Top artists:")
        for j, artist in enumerate(genre["artists"], 1):
            print(f"      {j}. {artist['artist']} ({artist['playcount']:,} plays)")


def analyze_genre(args):
    """Analyze a specific genre."""
    print(f"Analyzing your '{args.genre}' listening...")
    print("=" * 70)

    analyzer = GenreAnalyzer()
    artists = analyzer.analyze_top_artists_by_genre(
        genre=args.genre, limit=args.limit, top_n=args.top
    )

    if not artists:
        print(f"\nNo artists found for genre: {args.genre}")
        print("Try checking your spelling or using a more common genre tag.")
        return

    total_plays = sum(int(a.get("playcount", 0)) for a in artists)

    print(f"\nFound {len(artists)} artists in '{args.genre}'")
    print(f"Total plays: {total_plays:,}\n")
    print("=" * 70)
    print(f"TOP {len(artists)} ARTISTS IN {args.genre.upper()}")
    print("=" * 70)

    for i, artist in enumerate(artists, 1):
        print(f"\n{i}. {artist['artist']}")
        print(f"   Plays: {int(artist['playcount']):,}")
        print(f"   Tags: {', '.join(artist.get('tags', []))}")
        print(f"   URL: {artist.get('url', '')}")


def compare_genres(args):
    """Compare multiple genres."""
    print(f"Comparing genres: {', '.join(args.genres)}")
    print("=" * 70)

    analyzer = GenreAnalyzer()

    results = {}
    for genre in args.genres:
        print(f"\nAnalyzing {genre}...")
        artists = analyzer.analyze_top_artists_by_genre(genre, limit=args.limit, top_n=args.top)
        results[genre] = {
            "artists": artists,
            "total_plays": sum(int(a.get("playcount", 0)) for a in artists),
            "artist_count": len(artists),
        }

    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)

    for genre, data in results.items():
        print(f"\n{genre}:")
        print(f"  Artists found: {data['artist_count']}")
        print(f"  Total plays: {data['total_plays']:,}")
        if data["artists"]:
            top_playcount = int(data["artists"][0]["playcount"])
            print(f"  Top artist: {data['artists'][0]['artist']} ({top_playcount:,} plays)")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze Last.fm listening data by genre/tags",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all genres
  python genre_analysis.py list --top 20

  # Analyze a specific genre
  python genre_analysis.py analyze rock --top 15

  # Compare multiple genres
  python genre_analysis.py compare hip-hop jazz electronic --top 10
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser("list", help="List all genres")
    list_parser.add_argument(
        "--limit", type=int, default=100, help="Number of artists to analyze (default: 100)"
    )
    list_parser.add_argument(
        "--top", type=int, default=20, help="Number of top genres to show (default: 20)"
    )
    list_parser.set_defaults(func=list_all_genres)

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a specific genre")
    analyze_parser.add_argument("genre", help="Genre/tag to analyze")
    analyze_parser.add_argument(
        "--limit", type=int, default=100, help="Number of artists to search (default: 100)"
    )
    analyze_parser.add_argument(
        "--top", type=int, default=10, help="Number of top artists to show (default: 10)"
    )
    analyze_parser.set_defaults(func=analyze_genre)

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare multiple genres")
    compare_parser.add_argument("genres", nargs="+", help="Genres/tags to compare")
    compare_parser.add_argument(
        "--limit", type=int, default=100, help="Number of artists to search (default: 100)"
    )
    compare_parser.add_argument(
        "--top", type=int, default=10, help="Number of top artists per genre (default: 10)"
    )
    compare_parser.set_defaults(func=compare_genres)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
