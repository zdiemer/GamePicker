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

from excel_game import ExcelPlatform
from excel_loader import ExcelLoader
from match_validator import MatchValidator

from excel_backed_cache import ExcelBackedCache

MOBY_NAME_TO_SHEET_NAME: Dict[str, Set[ExcelPlatform] | ExcelPlatform] = {
    "3do": ExcelPlatform._3DO,
    "acorn 32-bit": set([ExcelPlatform.ACORN_ARCHIMEDES, ExcelPlatform.RISC_PC]),
    "amiga cd32": ExcelPlatform.COMMODORE_AMIGA_CD32,
    "amiga": ExcelPlatform.COMMODORE_AMIGA,
    "amstrad cpc": ExcelPlatform.AMSTRAD_CPC,
    "android": ExcelPlatform.ANDROID,
    "apple ii": ExcelPlatform.APPLE_II,
    "apple iigs": ExcelPlatform.APPLE_IIGS,
    "arcade": ExcelPlatform.ARCADE,
    "arcadia 2001": ExcelPlatform.ARCADIA_2001,
    "arduboy": ExcelPlatform.ARDUBOY,
    "atari 8-bit": ExcelPlatform.ATARI_8_BIT,
    "atari 2600": ExcelPlatform.ATARI_2600,
    "atari 5200": ExcelPlatform.ATARI_5200,
    "atari 7800": ExcelPlatform.ATARI_7800,
    "atari st": ExcelPlatform.ATARI_ST,
    "bbc micro": ExcelPlatform.BBC_MICRO,
    "blu-ray disc player": ExcelPlatform.DVD_PLAYER,
    "brew": ExcelPlatform.BREW,
    "browser": ExcelPlatform.BROWSER,
    "casio loopy": ExcelPlatform.CASIO_LOOPY,
    "cd-i": ExcelPlatform.PHILIPS_CD_I,
    "coleco adam": ExcelPlatform.COLECO_ADAM,
    "colecovision": ExcelPlatform.COLECOVISION,
    "commodore_16, plus/4": ExcelPlatform.COMMODORE_PLUS_4,
    "commodore 64": ExcelPlatform.COMMODORE_64,
    "commodore pet/cbm": ExcelPlatform.COMMODORE_PET,
    "dedicated console": ExcelPlatform.DEDICATED_CONSOLE,
    "dedicated handheld": ExcelPlatform.DEDICATED_CONSOLE,
    "doja": ExcelPlatform.DOJA,
    "dos": ExcelPlatform.PC,
    "dragon 32/64": ExcelPlatform.DRAGON_32_64,
    "dreamcast": ExcelPlatform.SEGA_DREAMCAST,
    "dvd player": ExcelPlatform.DVD_PLAYER,
    "electron": ExcelPlatform.ACORN_ELECTRON,
    "epoch super cassette vision": ExcelPlatform.EPOCH_SUPER_CASSETTE_VISION,
    "evercade": ExcelPlatform.EVERCADE,
    "exen": ExcelPlatform.EXEN,
    "exidy sorcerer": ExcelPlatform.EXIDY_SORCERER,
    "fire os": ExcelPlatform.AMAZON_FIRE_TV,
    "fm towns": ExcelPlatform.FM_TOWNS,
    "fm-7": ExcelPlatform.FM_7,
    "galaksija": ExcelPlatform.GALAKSIJA,
    "game boy advance": set([ExcelPlatform.E_READER, ExcelPlatform.GAME_BOY_ADVANCE]),
    "game boy color": ExcelPlatform.GAME_BOY_COLOR,
    "game boy": ExcelPlatform.GAME_BOY,
    "game.com": ExcelPlatform.GAME_COM,
    "game gear": ExcelPlatform.SEGA_GAME_GEAR,
    "gamecube": ExcelPlatform.NINTENDO_GAMECUBE,
    "genesis": ExcelPlatform.SEGA_GENESIS,
    "gizmondo": ExcelPlatform.GIZMONDO,
    "gp2x": ExcelPlatform.GP2X,
    "gp2x wiz": ExcelPlatform.GP2X_WIZ,
    "gp32": ExcelPlatform.GAMEPARK_32,
    "hyperscan": ExcelPlatform.HYPERSCAN,
    "intellivision": ExcelPlatform.INTELLIVISION,
    "ipad": ExcelPlatform.IOS,
    "iphone": ExcelPlatform.IOS,
    "j2me": ExcelPlatform.J2ME,
    "jaguar": set([ExcelPlatform.ATARI_JAGUAR, ExcelPlatform.ATARI_JAGUAR_CD]),
    "laseractive": ExcelPlatform.PIONEER_LASERACTIVE,
    "lynx": ExcelPlatform.ATARI_LYNX,
    "macintosh": ExcelPlatform.MAC_OS,
    "mainframe": ExcelPlatform.PDP_10,
    "mattel aquarius": ExcelPlatform.MATTEL_AQUARIUS,
    "microvision": ExcelPlatform.MICROVISION,
    "mophun": ExcelPlatform.MOPHUN,
    "msx": set([ExcelPlatform.MSX, ExcelPlatform.MSX2, ExcelPlatform.MSX_TURBO_R]),
    "n-gage": ExcelPlatform.N_GAGE,
    "n-gage (service)": ExcelPlatform.N_GAGE_2_0,
    "neo geo cd": ExcelPlatform.NEO_GEO_CD,
    "neo geo pocket color": ExcelPlatform.NEO_GEO_POCKET_COLOR,
    "neo geo pocket": ExcelPlatform.NEO_GEO_POCKET,
    "nes": ExcelPlatform.NES,
    "new nintendo 3ds": ExcelPlatform.NEW_NINTENDO_3DS,
    "nintendo 3ds": ExcelPlatform.NINTENDO_3DS,
    "nintendo 64": ExcelPlatform.NINTENDO_64,
    "nintendo ds": ExcelPlatform.NINTENDO_DS,
    "nintendo dsi": set([ExcelPlatform.NINTENDO_DSI, ExcelPlatform.DSIWARE]),
    "nintendo switch": ExcelPlatform.NINTENDO_SWITCH,
    "nuon": ExcelPlatform.NUON,
    "odyssey 2": ExcelPlatform.MAGNAVOX_ODYSSEY_2,
    "oric": ExcelPlatform.ORIC,
    "os/2": ExcelPlatform.OS_2,
    "ouya": ExcelPlatform.OUYA,
    "palm os": ExcelPlatform.PALM_OS,
    "pc-6001": ExcelPlatform.NEC_PC_6001,
    "pc-88": ExcelPlatform.NEC_PC_8801,
    "pc-98": ExcelPlatform.NEC_PC_9801,
    "pc-fx": ExcelPlatform.PC_FX,
    "pippin": ExcelPlatform.BANDAI_PIPPIN,
    "playdate": ExcelPlatform.PLAYDATE,
    "playdia": ExcelPlatform.PLAYDIA,
    "playstation 2": ExcelPlatform.PLAYSTATION_2,
    "playstation 3": ExcelPlatform.PLAYSTATION_3,
    "playstation 4": ExcelPlatform.PLAYSTATION_4,
    "playstation 5": ExcelPlatform.PLAYSTATION_5,
    "playstation": ExcelPlatform.PLAYSTATION,
    "pok mon mini": ExcelPlatform.NINTENDO_POKEMON_MINI,
    "ps vita": ExcelPlatform.PLAYSTATION_VITA,
    "psp": ExcelPlatform.PLAYSTATION_PORTABLE,
    "quest": ExcelPlatform.OCULUS_QUEST,
    "sega 32x": ExcelPlatform.SEGA_32X,
    "sega cd": ExcelPlatform.SEGA_CD,
    "sega master system": ExcelPlatform.SEGA_MASTER_SYSTEM,
    "sega pico": ExcelPlatform.SEGA_PICO,
    "sega saturn": ExcelPlatform.SEGA_SATURN,
    "sg-1000": ExcelPlatform.SEGA_SG_1000,
    "sharp x1": ExcelPlatform.SHARP_X1,
    "sharp x68000": ExcelPlatform.SHARP_X68000,
    "snes": set([ExcelPlatform.SNES, ExcelPlatform.BS_X]),
    "stadia": ExcelPlatform.GOOGLE_STADIA,
    "super a'can": ExcelPlatform.SUPER_ACAN,
    "supergrafx": ExcelPlatform.SUPERGRAFX,
    "supervision": ExcelPlatform.WATARA_SUPERVISION,
    "symbian": ExcelPlatform.SYMBIAN,
    "ti-99/4a": ExcelPlatform.TI_99_4A,
    "trs-80 coco": ExcelPlatform.TRS_80_COLOR_COMPUTER,
    "turbografx cd": ExcelPlatform.TURBOGRAFX_CD,
    "turbografx-16": ExcelPlatform.TURBOGRAFX_16,
    "tvos": ExcelPlatform.TVOS,
    "vic-20": ExcelPlatform.COMMODORE_VIC_20,
    "virtual boy": ExcelPlatform.VIRTUAL_BOY,
    "watchos": ExcelPlatform.WATCHOS,
    "wii u": ExcelPlatform.NINTENDO_WII_U,
    "wii": set([ExcelPlatform.NINTENDO_WII, ExcelPlatform.WIIWARE]),
    "windows 3.x": ExcelPlatform.PC,
    "windows 16-bit": ExcelPlatform.PC,
    "windows apps": ExcelPlatform.PC,
    "windows mobile": ExcelPlatform.WINDOWS_MOBILE,
    "windows phone": ExcelPlatform.WINDOWS_PHONE,
    "windows": ExcelPlatform.PC,
    "wonderswan color": ExcelPlatform.WONDERSWAN_COLOR,
    "wonderswan": ExcelPlatform.WONDERSWAN,
    "xbox 360": ExcelPlatform.XBOX_360,
    "xbox one": ExcelPlatform.XBOX_ONE,
    "xbox series": ExcelPlatform.XBOX_SERIES_X_S,
    "xbox": ExcelPlatform.XBOX,
    "zeebo": ExcelPlatform.ZEEBO,
    "zodiac": ExcelPlatform.TAPWAVE_ZODIAC,
    "zx spectrum": ExcelPlatform.ZX_SPECTRUM,
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

    def to_enum_name(plat: str) -> str:
        plat = plat.upper().strip().replace(" ", "_")
        if str.isnumeric(plat[0]):
            plat = f"_{plat}"
        return plat

    if cache_data is not None:
        games, _, _, _, _ = cache_data
    else:
        games = ExcelLoader().games

    platform = platform.lower().strip()

    if platform in MOBY_NAME_TO_SHEET_NAME or to_enum_name(platform) in [
        ep.name for ep in list(ExcelPlatform)
    ]:
        sheet_platform = (
            MOBY_NAME_TO_SHEET_NAME.get(platform)
            or ExcelPlatform[to_enum_name(platform)]
        )
    else:
        print(f"{platform} not found in MOBY_NAME_TO_SHEET_NAME")
        sheet_platform = None

    validator = MatchValidator()
    platform_games = set(
        validator.normalize(g.title)
        for g in filter(
            lambda g: (
                (g.platform == sheet_platform)
                if isinstance(sheet_platform, ExcelPlatform | None)
                else (g.platform in sheet_platform)
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
