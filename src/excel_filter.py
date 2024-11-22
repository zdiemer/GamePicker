import datetime

from excel_game import (
    ExcelGame,
    ExcelGenre,
    ExcelPlatform,
    Playability,
    TranslationStatus,
)

from picker_constants import HANDHELD_PLATFORMS
from picker_enums import PickerMode


class ExcelFilter:
    @staticmethod
    def included_in_mode(game: ExcelGame, mode: PickerMode) -> bool:
        if mode == PickerMode.HANDHELD:
            filtered_by_platform = game.platform in HANDHELD_PLATFORMS

            filtered_by_owned = filtered_by_platform and (
                game.platform
                not in (
                    ExcelPlatform.NINTENDO_3DS,
                    ExcelPlatform.DSIWARE,
                    ExcelPlatform.NINTENDO_SWITCH,
                )
                or game.owned
            )

            filtered_by_steam = filtered_by_owned and (
                game.platform != ExcelPlatform.PC
                or (
                    game.digital_platform == "Steam"
                    and not game.vr
                    and game.genre
                    not in (
                        ExcelGenre.REAL_TIME_STRATEGY,
                        ExcelGenre.FIRST_PERSON_SHOOTER,
                        ExcelGenre.TEXT_ADVENTURE,
                    )
                )
            )

            filtered_by_laserdisc = filtered_by_steam and (
                game.platform != ExcelPlatform.ARCADE
                or game.physical_media_format != "LaserDisc"
            )

            return filtered_by_laserdisc
        if mode == PickerMode.HIGH_PRIORITY:
            return (game.priority or 0) > 3 or game.combined_rating >= 0.8
        if mode == PickerMode.OWNED:
            return game.owned
        return True

    @staticmethod
    def is_not_low_priority(game: ExcelGame) -> bool:
        return (game.priority or 0) > 1

    @staticmethod
    def is_playable(game: ExcelGame) -> bool:
        return game.playability == Playability.PLAYABLE

    @staticmethod
    def is_playable_by_language(game: ExcelGame) -> bool:
        return (
            game.translation is None
            or game.translation != TranslationStatus.NONE
            or game.genre
            not in (
                ExcelGenre.ACTION_RPG,
                ExcelGenre.ADVENTURE,
                ExcelGenre.CARD_GAME,
                ExcelGenre.COMPUTER_RPG,
                ExcelGenre.DUNGEON_CRAWLER,
                ExcelGenre.STRATEGY_RPG,
                ExcelGenre.TURN_BASED_RPG,
                ExcelGenre.VISUAL_NOVEL,
                ExcelGenre.ACTION_ADVENTURE,
                ExcelGenre.TURN_BASED_STRATEGY,
                ExcelGenre.TURN_BASED_TACTICS,
                ExcelGenre.STRATEGY,
                ExcelGenre.MMORPG,
                ExcelGenre.REAL_TIME_TACTICS,
                ExcelGenre.ROGUELIKE,
                ExcelGenre.SIMULATION,
                ExcelGenre.SURVIVAL_HORROR,
                ExcelGenre.TEXT_ADVENTURE,
                ExcelGenre.TRIVIA,
            )
        )

    @staticmethod
    def is_unplayed(game: ExcelGame) -> bool:
        return not game.completed

    @staticmethod
    def is_released(game: ExcelGame) -> bool:
        return (
            game.release_date is not None
            and game.release_date <= datetime.datetime.now()
        )
