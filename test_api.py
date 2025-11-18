#!/usr/bin/env python3
"""Quick test script to verify Last.fm API works."""

from transformer.scrapers.lastfm_api import LastFMAPI

print("Testing Last.fm API...")
print("=" * 50)

api = LastFMAPI()

# Test get_top_artists
print("\n1. Testing get_top_artists...")
artists = api.get_top_artists(limit=5)
print(f"✓ Successfully fetched {len(artists)} top artists")
for i, artist in enumerate(artists[:3], 1):
    print(f"  {i}. {artist['artist']} ({artist['playcount']} plays)")

# Test get_recent_tracks
print("\n2. Testing get_recent_tracks...")
tracks = api.get_recent_tracks(limit=5)
print(f"✓ Successfully fetched {len(tracks)} recent tracks")
for i, track in enumerate(tracks[:3], 1):
    print(f"  {i}. {track['track']} by {track['artist']}")

# Test get_user_info
print("\n3. Testing get_user_info...")
user_info = api.get_user_info()
print(f"✓ Successfully fetched user info")
print(f"  User: {user_info['name']}")
print(f"  Total plays: {user_info['playcount']}")
print(f"  Country: {user_info['country']}")

# Test get_loved_tracks
print("\n4. Testing get_loved_tracks...")
loved = api.get_loved_tracks(limit=5)
print(f"✓ Successfully fetched {len(loved)} loved tracks")
for i, track in enumerate(loved[:3], 1):
    print(f"  {i}. {track['track']} by {track['artist']}")

print("\n" + "=" * 50)
print("All API tests passed! ✓")
