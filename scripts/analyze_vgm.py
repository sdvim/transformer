#!/usr/bin/env python3
"""Analyze Last.fm data to find top video game music soundtracks using genre tags."""

from transformer.utils.genre_analyzer import GenreAnalyzer

# VGM-related tags to search for
VGM_TAGS = [
    "video game music",
    "game",
    "soundtrack",
    "vgm",
    "video game",
    "game music",
    "nintendo",
    "chiptune",
    "8-bit",
    "16-bit",
]


def analyze_vgm_listening():
    """Analyze user's Last.fm data for video game music using tags."""
    print("Analyzing your Last.fm listening data for video game music...")
    print("=" * 70)

    analyzer = GenreAnalyzer()

    # Try multiple VGM-related tags
    print("\nSearching for VGM-tagged artists...")
    all_vgm_artists = {}

    for tag in VGM_TAGS:
        try:
            print(f"  Checking tag: '{tag}'...")
            artists = analyzer.analyze_top_artists_by_genre(tag, limit=200, top_n=50)

            for artist in artists:
                artist_name = artist["artist"]
                if artist_name not in all_vgm_artists:
                    all_vgm_artists[artist_name] = artist
                # Keep the one with higher playcount if duplicate
                elif int(artist["playcount"]) > int(all_vgm_artists[artist_name]["playcount"]):
                    all_vgm_artists[artist_name] = artist

        except Exception as e:
            print(f"  Warning: Could not process tag '{tag}': {e}")
            continue

    # Convert to list and sort by playcount
    vgm_artists = list(all_vgm_artists.values())
    vgm_artists.sort(key=lambda x: int(x.get("playcount", 0)), reverse=True)

    # Display top 10
    print("\n" + "=" * 70)
    print("YOUR TOP 10 VIDEO GAME MUSIC ARTISTS (BY TAGS)")
    print("=" * 70)

    if not vgm_artists:
        print("\nNo video game music found!")
        print("This might mean:")
        print("  1. VGM artists in your library aren't tagged properly on Last.fm")
        print("  2. You need to listen to more video game music!")
        return

    total_vgm_plays = sum(int(a.get("playcount", 0)) for a in vgm_artists)

    for i, artist in enumerate(vgm_artists[:10], 1):
        print(f"\n{i}. {artist['artist']}")
        print(f"   Plays: {int(artist['playcount']):,}")
        tags = artist.get("tags", [])
        if tags:
            print(f"   Tags: {', '.join(tags)}")
        print(f"   URL: {artist.get('url', '')}")

    # Statistics
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Total VGM artists found: {len(vgm_artists)}")
    print(f"Total VGM plays: {total_vgm_plays:,}")

    # Get total user plays for percentage
    user_info = analyzer.api.get_user_info()
    total_plays = int(user_info["playcount"])
    vgm_percentage = (total_vgm_plays / total_plays) * 100

    print(f"Total account plays: {total_plays:,}")
    print(f"VGM percentage: {vgm_percentage:.1f}%")

    # Show all VGM artists if there are more than 10
    if len(vgm_artists) > 10:
        print("\n" + "=" * 70)
        print(f"OTHER VGM ARTISTS IN YOUR LIBRARY ({len(vgm_artists) - 10} more)")
        print("=" * 70)
        for i, artist in enumerate(vgm_artists[10:20], 11):  # Show next 10
            print(f"{i}. {artist['artist']} ({int(artist['playcount']):,} plays)")

        if len(vgm_artists) > 20:
            print(f"\n... and {len(vgm_artists) - 20} more artists")


if __name__ == "__main__":
    analyze_vgm_listening()
