from excel_game import (
    ExcelGenre,
    ExcelPlatform,
)

from game_selector import GameSelector

DAD_GAMES = GameSelector(
    _filter=lambda g: (g.estimated_playtime or 0) > 0
    and (g.estimated_playtime or 0) <= 10
    and g.genre
    in set(
        [
            ExcelGenre.TURN_BASED_RPG,
            ExcelGenre.TURN_BASED_STRATEGY,
            ExcelGenre.TURN_BASED_TACTICS,
            ExcelGenre.ADVENTURE,
            ExcelGenre.PUZZLE,
            ExcelGenre.STRATEGY_RPG,
            ExcelGenre.VISUAL_NOVEL,
            ExcelGenre.DUNGEON_CRAWLER,
            ExcelGenre.COMPUTER_RPG,
        ]
    )
    and (
        g.platform
        in set(
            [
                ExcelPlatform._3DO,
                ExcelPlatform.ARDUBOY,
                ExcelPlatform.ATARI_2600,
                ExcelPlatform.ATARI_5200,
                ExcelPlatform.ATARI_7800,
                ExcelPlatform.ATARI_JAGUAR,
                ExcelPlatform.ATARI_JAGUAR_CD,
                ExcelPlatform.ATARI_LYNX,
                ExcelPlatform.BS_X,
                ExcelPlatform.COLECOVISION,
                ExcelPlatform.EVERCADE,
                ExcelPlatform.FAMICOM_DISK_SYSTEM,
                ExcelPlatform.GAME_BOY,
                ExcelPlatform.GAME_BOY_ADVANCE,
                ExcelPlatform.GAME_BOY_COLOR,
                ExcelPlatform.INTELLIVISION,
                ExcelPlatform.IOS,
                ExcelPlatform.NEO_GEO_POCKET,
                ExcelPlatform.NEO_GEO_POCKET_COLOR,
                ExcelPlatform.NES,
                ExcelPlatform.NINTENDO_64,
                ExcelPlatform.NINTENDO_DS,
                ExcelPlatform.NINTENDO_GAMECUBE,
                ExcelPlatform.NINTENDO_POKEMON_MINI,
                ExcelPlatform.PLAYDATE,
                ExcelPlatform.PLAYSTATION,
                ExcelPlatform.PLAYSTATION_2,
                ExcelPlatform.PLAYSTATION_4,
                ExcelPlatform.PLAYSTATION_5,
                ExcelPlatform.PLAYSTATION_NETWORK,
                ExcelPlatform.PLAYSTATION_PORTABLE,
                ExcelPlatform.SEGA_32X,
                ExcelPlatform.SEGA_CD,
                ExcelPlatform.SEGA_DREAMCAST,
                ExcelPlatform.SEGA_GAME_GEAR,
                ExcelPlatform.SEGA_GENESIS,
                ExcelPlatform.SEGA_MASTER_SYSTEM,
                ExcelPlatform.SEGA_SATURN,
                ExcelPlatform.SNES,
                ExcelPlatform.THUMBY,
                ExcelPlatform.THUMBY_COLOR,
                ExcelPlatform.TURBOGRAFX_16,
                ExcelPlatform.TURBOGRAFX_CD,
                ExcelPlatform.VIRTUAL_BOY,
                ExcelPlatform.WONDERSWAN,
                ExcelPlatform.WONDERSWAN_COLOR,
                ExcelPlatform.XBOX,
            ]
        )
        or (g.platform == ExcelPlatform.PC and g.digital_platform == "Steam")
        or (
            g.platform
            in set(
                [
                    ExcelPlatform.DEDICATED_CONSOLE,
                    ExcelPlatform.DSIWARE,
                    ExcelPlatform.NEW_NINTENDO_3DS,
                    ExcelPlatform.NINTENDO_3DS,
                    ExcelPlatform.NINTENDO_SWITCH,
                    ExcelPlatform.PLAYSTATION_VITA,
                    ExcelPlatform.XBOX_ONE,
                    ExcelPlatform.XBOX_SERIES_X_S,
                ]
            )
            and (g.owned or g.subscription_service is not None)
        )
    )
    and not g.vr
    and (g.combined_rating >= 75 or g.priority > 3),
    name="Dad Games",
)
