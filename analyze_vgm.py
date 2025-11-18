#!/usr/bin/env python3
"""Analyze Last.fm data to find top video game music soundtracks."""

from transformer.scrapers.lastfm_api import LastFMAPI

# Known video game composers and their notable works
VGM_COMPOSERS = {
    "光田康典": "Yasunori Mitsuda (Chrono Trigger, Xenogears, Chrono Cross)",
    "近藤浩治": "Koji Kondo (Super Mario, Zelda)",
    "植松伸夫": "Nobuo Uematsu (Final Fantasy)",
    "下村陽子": "Yoko Shimomura (Kingdom Hearts, Street Fighter II)",
    "増子司": "Tsukasa Masuko (Shin Megami Tensei)",
    "目黒将司": "Shoji Meguro (Persona series)",
    "崎元仁": "Hitoshi Sakimoto (Final Fantasy Tactics, Vagrant Story)",
    "伊藤賢治": "Kenji Ito (SaGa series)",
    "菊田裕樹": "Hiroki Kikuta (Secret of Mana)",
    "古代祐三": "Yuzo Koshiro (Streets of Rage, Ys)",
    "すぎやまこういち": "Koichi Sugiyama (Dragon Quest)",
    "Nobuo Uematsu": "Final Fantasy series",
    "Koji Kondo": "Super Mario, Zelda",
    "Yasunori Mitsuda": "Chrono Trigger, Xenogears",
    "Yoko Shimomura": "Kingdom Hearts, Street Fighter II",
    "Shoji Meguro": "Persona series",
    "Toby Fox": "Undertale, Deltarune",
    "C418": "Minecraft",
    "Lena Raine": "Celeste, Minecraft",
    "Darren Korb": "Bastion, Hades, Transistor",
    "Austin Wintory": "Journey, Abzu",
    "Jesper Kyd": "Assassin's Creed, Hitman",
    "Jeremy Soule": "The Elder Scrolls, Guild Wars",
    "Inon Zur": "Fallout, Dragon Age",
    "Grant Kirkhope": "Banjo-Kazooie, GoldenEye 007",
    "David Wise": "Donkey Kong Country",
    "Michiru Yamane": "Castlevania series",
    "Akira Yamaoka": "Silent Hill series",
    "Keiichi Okabe": "NieR series",
    "Yuka Kitamura": "Dark Souls, Bloodborne",
    "Mick Gordon": "DOOM, Wolfenstein",
    "Jessica Curry": "Dear Esther, Everybody's Gone to the Rapture",
    "Christopher Larkin": "Hollow Knight",
    "Disasterpeace": "FEZ, Hyper Light Drifter",
    "Jake Kaufman": "Shovel Knight, Shantae",
    "Manami Matsumae": "Mega Man",
    "Hippo Campus": None,  # Not VGM, but might appear
}

# Common VGM-related keywords
VGM_KEYWORDS = [
    "soundtrack",
    "ost",
    "game",
    "video game",
    "gaming",
    "nintendo",
    "square enix",
    "capcom",
    "sega",
    "konami",
    "atlus",
    "pokemon",
    "zelda",
    "mario",
    "final fantasy",
    "persona",
    "chrono",
    "kingdom hearts",
    "mega man",
    "sonic",
    "castlevania",
    "metroid",
    "fire emblem",
]


def is_vgm_artist(artist_name: str, mbid: str = None) -> tuple[bool, str]:
    """
    Determine if an artist is a video game composer.

    Returns: (is_vgm, description)
    """
    name_lower = artist_name.lower()

    # Check against known composers
    if artist_name in VGM_COMPOSERS:
        description = VGM_COMPOSERS[artist_name] or artist_name
        return True, description

    # Check for common keywords
    for keyword in VGM_KEYWORDS:
        if keyword in name_lower:
            return True, artist_name

    return False, None


def analyze_vgm_listening():
    """Analyze user's Last.fm data for video game music."""
    print("Analyzing your Last.fm listening data for video game music...")
    print("=" * 70)

    api = LastFMAPI()

    # Fetch a large number of top artists to get good coverage
    print("\nFetching your top artists...")
    artists = api.get_top_artists(limit=200)
    print(f"Retrieved {len(artists)} artists")

    # Filter for VGM artists
    vgm_artists = []
    for artist in artists:
        is_vgm, description = is_vgm_artist(artist["artist"], artist.get("mbid"))
        if is_vgm:
            vgm_artists.append({
                "artist": artist["artist"],
                "playcount": int(artist["playcount"]),
                "description": description,
                "url": artist["url"],
            })

    # Sort by playcount
    vgm_artists.sort(key=lambda x: x["playcount"], reverse=True)

    # Display top 10
    print("\n" + "=" * 70)
    print("YOUR TOP 10 VIDEO GAME MUSIC SOUNDTRACKS")
    print("=" * 70)

    if not vgm_artists:
        print("\nNo video game music found in your top artists!")
        print("You might want to check if the composers are under different names.")
        return

    total_vgm_plays = sum(a["playcount"] for a in vgm_artists)

    for i, artist in enumerate(vgm_artists[:10], 1):
        print(f"\n{i}. {artist['artist']}")
        print(f"   Plays: {artist['playcount']:,}")
        if artist['description'] != artist['artist']:
            print(f"   Known for: {artist['description']}")
        print(f"   URL: {artist['url']}")

    # Statistics
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Total VGM artists found: {len(vgm_artists)}")
    print(f"Total VGM plays: {total_vgm_plays:,}")

    # Get total user plays for percentage
    user_info = api.get_user_info()
    total_plays = int(user_info["playcount"])
    vgm_percentage = (total_vgm_plays / total_plays) * 100

    print(f"Total account plays: {total_plays:,}")
    print(f"VGM percentage: {vgm_percentage:.1f}%")

    # Show all VGM artists if there are more than 10
    if len(vgm_artists) > 10:
        print("\n" + "=" * 70)
        print("OTHER VGM ARTISTS IN YOUR LIBRARY")
        print("=" * 70)
        for i, artist in enumerate(vgm_artists[10:], 11):
            print(f"{i}. {artist['artist']} ({artist['playcount']:,} plays)")


if __name__ == "__main__":
    analyze_vgm_listening()
