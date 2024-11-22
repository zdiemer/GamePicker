from typing import Dict, List
import os
import re

from pathlib import Path

from excel_game import ExcelGame, ExcelPlatform
from game_match import DataSource, GameMatch

from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from output_parser import OutputParser
from picker_enums import PickerMode


def non_downloaded_games(
    games: List[ExcelGame], data_provider: DataProvider
) -> List[ExcelGame]:
    by_platform = GameGrouping().get_groups(games)
    pattern = r"(\(.*\))|(\[.*\])|([vV]{1}[0-9]{1}\.[0-9]{1})|(_.*)|(, The)"
    non_downloaded = []

    arcade_database_output: Dict[str, GameMatch] = {}

    for platform, p_games in by_platform.items():
        folders = []

        # Atari
        if platform == ExcelPlatform.ATARI_8_BIT:
            folders.append("E:\\Emulation\\Atari\\Atari 8-bit")
        if platform == ExcelPlatform.ATARI_2600:
            folders.append("E:\\Emulation\\Atari\\Atari 2600")
        if platform == ExcelPlatform.ATARI_5200:
            folders.append("E:\\Emulation\\Atari\\Atari 5200")
        if platform == ExcelPlatform.ATARI_7800:
            folders.append("E:\\Emulation\\Atari\\Atari 7800")
        if platform == ExcelPlatform.ATARI_JAGUAR:
            folders.append("E:\\Emulation\\Atari\\Atari Jaguar")
        if platform == ExcelPlatform.ATARI_JAGUAR_CD:
            folders.append("E:\\Emulation\\Atari\\Atari Jaguar CD")
        if platform == ExcelPlatform.ATARI_LYNX:
            folders.append("E:\\Emulation\\Atari\\Atari Lynx")
        if platform == ExcelPlatform.ATARI_ST:
            folders.append("E:\\Emulation\\Atari\\Atari ST")

        # Commodore
        if platform == ExcelPlatform.COMMODORE_64:
            folders.extend(
                [
                    "E:\\Emulation\\Commodore\\Commodore 64",
                    "D:\\itch.io\\Commodore 64",
                ]
            )
        if platform == ExcelPlatform.COMMODORE_AMIGA:
            folders.append("E:\\Emulation\\Commodore\\Commodore Amiga")
        if platform == ExcelPlatform.COMMODORE_AMIGA_CD32:
            folders.append("E:\\Emulation\\Commodore\\Commodore Amiga CD32")
        if platform == ExcelPlatform.COMMODORE_PLUS_4:
            folders.append("E:\\Emulation\\Commodore\\Commodore Plus 4")
        if platform == ExcelPlatform.COMMODORE_VIC_20:
            folders.append("E:\\Emulation\\Commodore\\Commodore VIC-20")

        # Microsoft
        if platform == ExcelPlatform.XBOX:
            folders.append("E:\\Emulation\\Microsoft\\Xbox")
        if platform == ExcelPlatform.XBOX_360:
            folders.append("E:\\Emulation\\Microsoft\\Xbox 360")

        # Nintendo
        if platform == ExcelPlatform.FAMICOM_DISK_SYSTEM:
            folders.append("E:\\Emulation\\Nintendo\\Famicom Disk System")
        if platform == ExcelPlatform.GAME_BOY:
            folders.append("E:\\Emulation\\Nintendo\\Game Boy")
        if platform == ExcelPlatform.GAME_BOY_ADVANCE:
            folders.append("E:\\Emulation\\Nintendo\\Game Boy Advance")
        if platform == ExcelPlatform.GAME_BOY_COLOR:
            folders.append("E:\\Emulation\\Nintendo\\Game Boy Color")
        if platform == ExcelPlatform.NINTENDO_GAMECUBE:
            folders.append("E:\\Emulation\\Nintendo\\GameCube")
        if platform == ExcelPlatform.NES:
            folders.extend(
                [
                    "E:\\Emulation\\Nintendo\\NES\\Famicom",
                    "E:\\Emulation\\Nintendo\\NES\\Nintendo Entertainment System",
                    "D:\\itch.io\\NES",
                ]
            )
        if platform == ExcelPlatform.NINTENDO_3DS:
            folders.append("E:\\Emulation\\Nintendo\\Nintendo 3DS")
        if platform == ExcelPlatform.NINTENDO_64:
            folders.append("E:\\Emulation\\Nintendo\\Nintendo 64")
        if platform == ExcelPlatform.NINTENDO_64DD:
            folders.append("E:\\Emulation\\Nintendo\\Nintendo 64DD")
        if platform == ExcelPlatform.NINTENDO_DS:
            folders.append("E:\\Emulation\\Nintendo\\Nintendo DS")
        if platform == ExcelPlatform.DSIWARE:
            folders.append("E:\\Emulation\\Nintendo\\Nintendo DS\\DSiWare")
        if platform == ExcelPlatform.NINTENDO_DSI:
            folders.append("E:\\Emulation\\Nintendo\\Nintendo DS\\Nintendo DSi")
        if platform == ExcelPlatform.NINTENDO_POKEMON_MINI:
            folders.append("E:\\Emulation\\Nintendo\\Nintendo Pokémon mini")
        if platform == ExcelPlatform.SNES:
            folders.extend(
                [
                    "E:\\Emulation\\Nintendo\\SNES\\Nintendo Power",
                    "E:\\Emulation\\Nintendo\\SNES\\Super Famicom",
                    "E:\\Emulation\\Nintendo\\SNES\\Super Nintendo Entertainment System",
                ]
            )
        if platform == ExcelPlatform.BS_X:
            folders.append("E:\\Emulation\\Nintendo\\SNES\\Satellaview")
        if platform == ExcelPlatform.VIRTUAL_BOY:
            folders.append("E:\\Emulation\\Nintendo\\Virtual Boy")
        if platform == ExcelPlatform.NINTENDO_WII:
            folders.append("E:\\Emulation\\Nintendo\\Wii")
        if platform == ExcelPlatform.WIIWARE:
            folders.append("E:\\Emulation\\Nintendo\\Wii\\WiiWare")
        if platform == ExcelPlatform.NINTENDO_WII_U:
            folders.append("E:\\Emulation\\Nintendo\\Wii U")

        # Other
        if platform == ExcelPlatform._3DO:
            folders.append("E:\\Emulation\\Other\\3DO")
        if platform == ExcelPlatform.ACORN_ARCHIMEDES:
            folders.append("E:\\Emulation\\Other\\Acorn Archimedes")
        if platform == ExcelPlatform.RISC_PC:
            folders.append("E:\\Emulation\\Other\\Acorn Archimedes")
        if platform == ExcelPlatform.ACORN_ELECTRON:
            folders.append("E:\\Emulation\\Other\\Acorn Electron")
        if platform == ExcelPlatform.AMSTRAD_CPC:
            folders.append("E:\\Emulation\\Other\\Amstrad CPC")
        if platform == ExcelPlatform.ANDROID:
            folders.extend(["E:\\Emulation\\Other\\Android", "D:\\itch.io\\Android"])
        if platform == ExcelPlatform.APPLE_II:
            folders.append("E:\\Emulation\\Other\\Apple II")
        if platform == ExcelPlatform.ARCADE:
            folders.extend(
                [
                    "E:\\Emulation\\Other\\Arcade (Non-MAME)",
                    "E:\\Emulation\\Other\\MAME",
                ]
            )

            arcade_database_output = OutputParser.get_source_output(
                DataSource.ARCADE_DATABASE
            )
        if platform == ExcelPlatform.BBC_MICRO:
            folders.append("E:\\Emulation\\Other\\BBC Micro")
        if platform == ExcelPlatform.COLECOVISION:
            folders.append("E:\\Emulation\\Other\\ColecoVision")
        if platform == ExcelPlatform.DEDICATED_CONSOLE:
            folders.append("E:\\Emulation\\Other\\Dedicated Console")
        if platform == ExcelPlatform.EPOCH_SUPER_CASSETTE_VISION:
            folders.append("E:\\Emulation\\Other\\Epoch Super Cassette Vision")
        if platform == ExcelPlatform.FM_TOWNS:
            folders.append("E:\\Emulation\\Other\\FM Towns")
        if platform == ExcelPlatform.FM_7:
            folders.append("E:\\Emulation\\Other\\FM-7")
        if platform == ExcelPlatform.GAMEPARK_32:
            folders.append("E:\\Emulation\\Other\\GamePark 32")
        if platform == ExcelPlatform.INTELLIVISION:
            folders.append("E:\\Emulation\\Other\\Intellivision")
        if platform == ExcelPlatform.J2ME:
            folders.extend(
                [
                    "E:\\Emulation\\Other\\J2ME",
                    "E:\\Emulation\\Other\\J2ME\\call-of-duty-java-collection_202012",
                ]
            )
        if platform == ExcelPlatform.MSX:
            folders.append("E:\\Emulation\\Other\\MSX\\MSX")
        if platform == ExcelPlatform.MSX2:
            folders.append("E:\\Emulation\\Other\\MSX\\MSX2")
        if platform == ExcelPlatform.MSX_TURBO_R:
            folders.append("E:\\Emulation\\Other\\MSX\\MSX Turbo-R")
        if platform == ExcelPlatform.NEC_PC_8801:
            folders.append("E:\\Emulation\\Other\\NEC PC-8801")
        if platform == ExcelPlatform.NEC_PC_9801:
            folders.append("E:\\Emulation\\Other\\NEC PC-9801")
        if platform == ExcelPlatform.NEO_GEO_CD:
            folders.append("E:\\Emulation\\Other\\Neo-Geo CD")
        if platform == ExcelPlatform.NEO_GEO_POCKET:
            folders.append("E:\\Emulation\\Other\\Neo-Geo Pocket")
        if platform == ExcelPlatform.NEO_GEO_POCKET_COLOR:
            folders.append("E:\\Emulation\\Other\\Neo-Geo Pocket")
        if platform == ExcelPlatform.N_GAGE:
            folders.append("E:\\Emulation\\Other\\N-Gage")
        if platform == ExcelPlatform.N_GAGE_2_0:
            folders.append("E:\\Emulation\\Other\\N-Gage")
        if platform == ExcelPlatform.PC_FX:
            folders.append("E:\\Emulation\\Other\\PC-FX")
        if platform == ExcelPlatform.PHILIPS_CD_I:
            folders.append("E:\\Emulation\\Other\\Philips CD-i")
        if platform == ExcelPlatform.SHARP_X1:
            folders.append("E:\\Emulation\\Other\\Sharp X1")
        if platform == ExcelPlatform.SHARP_X68000:
            folders.append("E:\\Emulation\\Other\\Sharp X68000")
        if platform == ExcelPlatform.SUPERGRAFX:
            folders.append("E:\\Emulation\\Other\\SuperGrafx")
        if platform == ExcelPlatform.GAME_COM:
            folders.append("E:\\Emulation\\Other\\Tiger Game.com")
        if platform == ExcelPlatform.TRS_80_COLOR_COMPUTER:
            folders.append("E:\\Emulation\\Other\\TRS-80 Color Computer")
        if platform == ExcelPlatform.TURBOGRAFX_16:
            folders.append("E:\\Emulation\\Other\\TurboGrafx-16\\TurboGrafx-16")
        if platform == ExcelPlatform.TURBOGRAFX_CD:
            folders.append("E:\\Emulation\\Other\\TurboGrafx-16\\TurboGrafx-CD")
        if platform == ExcelPlatform.VECTREX:
            folders.append("E:\\Emulation\\Other\\Vectrex")
        if platform == ExcelPlatform.WATARA_SUPERVISION:
            folders.append("E:\\Emulation\\Other\\Watara SuperVision")
        if platform == ExcelPlatform.WONDERSWAN:
            folders.append("E:\\Emulation\\Other\\WonderSwan\\WonderSwan")
        if platform == ExcelPlatform.WONDERSWAN_COLOR:
            folders.append("E:\\Emulation\\Other\\WonderSwan\\WonderSwan Color")
        if platform == ExcelPlatform.ZEEBO:
            folders.append("E:\\Emulation\\Other\\Zeebo")
        if platform == ExcelPlatform.ZX_SPECTRUM:
            folders.append("E:\\Emulation\\Other\\ZX Spectrum")

        # Sega
        if platform == ExcelPlatform.SEGA_DREAMCAST:
            folders.append("E:\\Emulation\\Sega\\Dreamcast")
        if platform == ExcelPlatform.SEGA_GAME_GEAR:
            folders.append("E:\\Emulation\\Sega\\Game Gear")
        if platform == ExcelPlatform.SEGA_SATURN:
            folders.append("E:\\Emulation\\Sega\\Saturn")
        if platform == ExcelPlatform.SEGA_GENESIS:
            folders.extend(
                [
                    "E:\\Emulation\\Sega\\Sega Genesis\\Genesis",
                    "D:\\itch.io\\Genesis",
                ]
            )
        if platform == ExcelPlatform.SEGA_32X:
            folders.append("E:\\Emulation\\Sega\\Sega Genesis\\Sega 32X")
        if platform == ExcelPlatform.SEGA_CD:
            folders.append("E:\\Emulation\\Sega\\Sega Genesis\\Sega CD")
        if platform == ExcelPlatform.SEGA_MASTER_SYSTEM:
            folders.append("E:\\Emulation\\Sega\\Sega Master System")
        if platform == ExcelPlatform.SEGA_SG_1000:
            folders.append("E:\\Emulation\\Sega\\Sega SG-1000")

        # Sony
        if platform == ExcelPlatform.PLAYSTATION:
            folders.append("E:\\Emulation\\Sony\\PlayStation")
        if platform == ExcelPlatform.PLAYSTATION_2:
            folders.append("E:\\Emulation\\Sony\\PlayStation 2")
        if platform == ExcelPlatform.PLAYSTATION_3:
            folders.append("E:\\Emulation\\Sony\\PlayStation 3")
        if platform == ExcelPlatform.PLAYSTATION_PORTABLE:
            folders.append("E:\\Emulation\\Sony\\PlayStation Portable")
        if platform == ExcelPlatform.PLAYSTATION_VITA:
            folders.append("E:\\Emulation\\Sony\\PlayStation Vita")

        # PC

        if platform == ExcelPlatform.PC:
            folders.extend(
                [
                    "E:\\Emulation\\Other\\MS-DOS",
                    "D:\\Abandonware",
                    "D:\\DRM Free",
                    "D:\\Freeware",
                    "D:\\itch.io\\PC",
                ]
            )

        # itch.io
        if platform == ExcelPlatform.PLAYDATE:
            folders.append("D:\\itch.io\\Playdate")

        if any(folders):
            downloaded = set([])
            for folder in folders:
                for _, subfolders, files in os.walk(folder):
                    for file in files:
                        if file == "desktop.ini":
                            continue
                        file_name = (
                            re.sub(pattern, "", Path(file).stem)
                            .strip()
                            .replace(" - ", ": ")
                        )
                        downloaded.add(file_name)
                    for subfolder in subfolders:
                        folder_name = (
                            re.sub(pattern, "", subfolder).strip().replace(" - ", ": ")
                        )
                        downloaded.add(folder_name)
                    break

            for game in p_games:
                should_check = (
                    game.game.platform == ExcelPlatform.PC
                    and (
                        not game.game.notes
                        or game.game.notes in ("Freeware", "DRM Free", "itch.io")
                    )
                ) or game.game.notes == "itch.io"
                if game.game.owned and not should_check:
                    continue

                matched = False

                for d_game in downloaded:
                    if (
                        game.game.platform == ExcelPlatform.ARCADE
                        and game.game.hash_id in arcade_database_output
                    ):
                        arcade_db_game = arcade_database_output[game.game.hash_id]
                        mame_name = arcade_db_game.match_info["game_name"]

                        if mame_name == d_game:
                            matched = True
                            break

                    if data_provider.get_validator().titles_equal_fuzzy(
                        d_game, game.game.normal_title
                    ):
                        matched = True
                        break

                if not matched:
                    non_downloaded.append(game.game)
        else:
            non_downloaded.extend(
                list(filter(lambda g: not g.owned, [p.game for p in p_games]))
            )

    return non_downloaded


def get_non_downloaded_games_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        lambda games: non_downloaded_games(games, data_provider),
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
        skip_unless_specified=True,
        no_force=True,
        grouping=GameGrouping(should_rank=False),
        include_platform=False,
        name="Non-Downloaded Games",
    )
