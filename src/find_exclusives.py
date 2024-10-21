import asyncio
import inspect
import json
import os
import re
import sys
from typing import Dict, List, Set

from clients import (
    AlternateTitle,
    Cover,
    DatePart,
    Game,
    GamePlatform,
    Genre,
    GenreCategory,
    MobyGamesClient,
    Platform,
    RateLimit,
    Screenshot,
)
from excel_backed_cache import ExcelBackedCache
from excel_loader import ExcelLoader
from match_validator import MatchValidator

MOBY_NAME_TO_SHEET_NAME: Dict[str, Set[str] | str] = {
    "acorn 32-bit": set(["acorn archimedes", "risc pc"]),
    "amiga cd32": "commodore amiga cd32",
    "amiga": "commodore amiga",
    "cd-i": "philips cd-i",
    "commodore_16, plus/4": "commodore plus/4",
    "dos": "pc",
    "dreamcast": "sega dreamcast",
    "electron": "acorn electron",
    "gamecube": "nintendo gamecube",
    "game gear": "sega game gear",
    "genesis": "sega genesis",
    "gp32": "gamepark 32",
    "ipad": "ios",
    "iphone": "ios",
    "jaguar": set(["atari jaguar", "atari jaguar cd"]),
    "laseractive": "pioneer laseractive",
    "lynx": "atari lynx",
    "macintosh": "mac os",
    "msx": set(["msx", "msx2", "msx2+", "msx turbo r"]),
    "n-gage (service)": "n-gage 2.0",
    "neo geo cd": "neo-geo cd",
    "neo geo pocket color": "neo-geo pocket color",
    "neo geo pocket": "neo-geo pocket",
    "pc-6001": "nec pc-6001",
    "pc-88": "nec pc-8801",
    "pc-98": "nec pc-9801",
    "pok mon mini": "nintendo pokémon mini",
    "ps vita": "playstation vita",
    "psp": "playstation portable",
    "quest": "oculus quest",
    "sg-1000": "sega sg-1000",
    "snes": set(["snes", "bs-x"]),
    "supervision": "watara supervision",
    "trs-80 coco": "trs-80 color computer",
    "turbografx cd": "turbografx-cd",
    "vic-20": "commodore vic-20",
    "wii u": "nintendo wii u",
    "wii": set(["nintendo wii", "wiiware"]),
    "windows 3.x": "pc",
    "windows apps": "pc",
    "windows": "pc",
    "xbox series": "xbox series x|s",
    "zodiac": "tapwave zodiac",
}


def platform_to_file_name(platform: str) -> str:
    clean_name = re.sub(r"[^A-Za-z0-9-_]", "_", platform).lower()
    return f"exclusives/{clean_name}.json"


async def get_games(
    client: MobyGamesClient, platform_id: int, offset: int = 0
) -> List[Game]:
    print(f"Requesting games for platform {platform_id}, offset {offset}")
    return await client.games(platform_ids=[platform_id], offset=offset)


async def get_games_batch(client: MobyGamesClient, platform_id: int) -> List[Game]:
    games = await get_games(client, platform_id)
    game_len = len(games)
    last_game_len = 0

    offset = 100
    while game_len != last_game_len and len(games) % 100 == 0:
        games.extend(await get_games(client, platform_id, offset))
        offset += 100

    return games


async def find_exclusives(platform: str) -> List[Game]:
    file_path = platform_to_file_name(platform)

    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            games_json = json.loads(f.read())

            return [
                Game(
                    (
                        [
                            AlternateTitle(alt["description"], alt["title"])
                            for alt in game["alternate_titles"]
                        ]
                        if game.get("alternate_titles") is not None
                        else []
                    ),
                    game["description"],
                    game["id"],
                    [
                        Genre(
                            GenreCategory(
                                genre["category"]["name"], genre["category"]["id"]
                            ),
                            genre["id"],
                            genre["name"],
                        )
                        for genre in game["genres"]
                    ],
                    game["moby_score"],
                    game["moby_url"],
                    game["num_votes"],
                    game["official_url"],
                    [
                        GamePlatform(
                            Platform(_platform[0]["id"], _platform[0]["name"]),
                            _platform[1],
                        )
                        for _platform in game["platforms"]
                    ],
                    (
                        Cover(
                            game["sample_cover"]["height"],
                            game["sample_cover"]["image_url"],
                            game["sample_cover"]["platforms"],
                            game["sample_cover"]["thumbnail_image_url"],
                            game["sample_cover"]["width"],
                        )
                        if game.get("sample_cover") is not None
                        else None
                    ),
                    [
                        Screenshot(
                            screenshot["caption"],
                            screenshot["height"],
                            screenshot["image_url"],
                            screenshot["thumbnail_image_url"],
                            screenshot["width"],
                        )
                        for screenshot in game["sample_screenshots"]
                    ],
                    game["title"],
                )
                for game in filter(
                    lambda g: not any(
                        genre["name"].lower()
                        in ("add-on", "compilation", "special edition")
                        or genre["category"]["name"].lower()
                        in ("add-on", "special edition")
                        for genre in g["genres"]
                    ),
                    games_json,
                )
            ]

    client = MobyGamesClient(MatchValidator(), rate_limit=RateLimit(1, DatePart.SECOND))

    platforms = await client.platforms()

    moby_platform = next(
        filter(lambda p: p.name.lower() == platform.lower().strip(), platforms), None
    )

    if moby_platform is None:
        print(f"Could not find the platform '{platform}'")
        return []

    all_platform_games = await get_games_batch(client, moby_platform.id)
    print(f"{len(all_platform_games)} total games for {platform}")

    return list(
        filter(
            lambda g: len(g.platforms) == 1
            and not any(
                genre.name.lower() in ("add-on", "compilation", "special edition")
                or genre.category.name.lower() in ("add-on", "special edition")
                for genre in g.genres
            ),
            all_platform_games,
        )
    )


async def find_all_exclusives():
    client = MobyGamesClient(MatchValidator())

    platforms = await client.platforms()

    for platform in platforms:
        file_path = platform_to_file_name(platform.name)

        if os.path.isfile(file_path):
            continue

        print(f"Requesting all games for {platform.name}")

        all_platform_games = await get_games_batch(client, platform.id)

        platform_exclusives = list(
            filter(lambda g: len(g.platforms) == 1, all_platform_games)
        )

        if not any(platform_exclusives):
            continue

        if not os.path.exists("exclusives"):
            os.mkdir("exclusives")

        print(f"Writing {len(platform_exclusives)} exclusive games to {file_path}")

        if not os.path.isfile(file_path):
            with open(file_path, "w", encoding="utf-8"):
                pass

        with open(file_path, "r+", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    [g.__dict__ for g in platform_exclusives],
                    sort_keys=True,
                    indent=4,
                    default=lambda c: (
                        c.__dict__ if inspect.isclass(type(c)) else str(c)
                    ),
                )
            )


async def find_exclusives_missing(platform: str):
    cache_data = ExcelBackedCache().load("cache.pkl")
    games = None

    if cache_data is not None:
        games, _, _, _, _ = cache_data
    else:
        games = ExcelLoader().games

    platform = platform.lower().strip()

    sheet_platform_name = MOBY_NAME_TO_SHEET_NAME.get(platform) or platform

    validator = MatchValidator()
    platform_games = set(
        validator.normalize(g.title)
        for g in filter(
            lambda g: (
                (g.platform.value.lower() == sheet_platform_name)
                if isinstance(sheet_platform_name, str)
                else (g.platform.value.lower() in sheet_platform_name)
            ),
            games,
        )
    )

    _exclusives = await find_exclusives(platform)

    missing_exclusives = list(
        filter(
            lambda g: not any(
                gr.name in ("Gambling", "Racing / Driving", "Sports") for gr in g.genres
            )
            and validator.normalize(g.title) not in platform_games,
            _exclusives,
        )
    )

    return missing_exclusives


if __name__ == "__main__":
    if len(sys.argv) == 1:
        asyncio.run(find_all_exclusives())
    else:
        exclusives = asyncio.run(find_exclusives_missing(sys.argv[1]))

        if not any(exclusives):
            print(f"No exclusives for {sys.argv[1]}")
        else:
            print("")
            for i, g in enumerate(
                sorted(
                    exclusives, key=lambda g: (-(g.moby_score or 0), g.title.casefold())
                )
            ):
                moby_score = (
                    f" - {g.moby_score}"
                    if g.moby_score is not None and g.moby_score > 0
                    else ""
                )
                print(
                    f"{g.title} [{g.platforms[0].first_release_date}] ({g.moby_url}){moby_score}"
                )
                if (i + 1) % 100 == 0:
                    input(
                        f"{i + 1}/{len(exclusives)} listed. Press enter to continue.\n\n"
                    )
