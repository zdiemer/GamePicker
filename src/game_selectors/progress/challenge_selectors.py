from typing import Any, Callable, List, Optional
import datetime

from excel_game import ExcelGame, ExcelOwnedFormat, ExcelPlatform, ExcelRegion
from game_match import DataSource
from data_provider import DataProvider
from game_grouping import GameGrouping, GameGroups
from game_selector import GameSelector
from output_parser import OutputParser
from picker_enums import PickerMode

CHALLENGE_START: datetime.datetime = datetime.datetime(2024, 10, 20)


def get_platform_completion_id(game: ExcelGame) -> str:
    # One Per PC / Playdate Subplatform
    if (
        game.platform in (ExcelPlatform.PC, ExcelPlatform.PLAYDATE)
        and game.digital_platform is not None
    ):
        vr = " (VR)" if game.vr else ""
        dlc = " (DLC)" if game.dlc else ""
        return f"{game.platform.value} ({game.digital_platform}){vr}{dlc}"

    # DLC
    if game.dlc:
        return f"{game.platform.value} (DLC)"

    # MAME and Non-Mame
    if game.platform == ExcelPlatform.ARCADE:
        mame_games = OutputParser.get_source_output(DataSource.ARCADE_DATABASE)
        if game.hash_id in mame_games or game.release_year <= 2002:
            return f"{game.platform.value} (MAME)"
        return f"{game.platform.value} (Non-MAME)"

    # PS VR
    if game.platform == ExcelPlatform.PLAYSTATION_4 and game.vr:
        return f"{game.platform.value} VR"

    # Famicom / NES
    if game.platform == ExcelPlatform.NES:
        if game.release_region == ExcelRegion.JAPAN:
            return f"{game.platform.value} (Famicom)"
        if game.notes == "Bootleg":
            return f"{game.platform.value} (Bootleg)"

    # Super Famicom / SNES / Nintendo Power
    if (
        game.platform == ExcelPlatform.SNES
        and game.release_region == ExcelRegion.JAPAN
        and game.required_accessory is None
    ):
        return f"{game.platform.value} (Super Famicom)"

    if game.subscription_service is not None:
        return f"{game.platform.value} ({game.subscription_service})"

    # Digital / Retail Xbox 360 / XBLIG
    if game.platform == ExcelPlatform.XBOX_360:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.digital_platform == "Xbox Live Indie Games":
            return f"{game.platform.value} ({game.notes})"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (XBLA)"
        return f"{game.platform.value} (Emulation)"

    # Digital / Retail Xbox One
    if game.platform == ExcelPlatform.XBOX_ONE:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (Digital)"
        return f"{game.platform.value} (Emulation)"

    # Digital / Retail Xbox Series
    if game.platform == ExcelPlatform.XBOX_SERIES_X_S:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (Digital)"
        return f"{game.platform.value} (Emulation)"

    # Digital / Retail PS3
    if game.platform == ExcelPlatform.PLAYSTATION_3:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (PSN)"
        return f"{game.platform.value} (Emulation)"

    # Digital / Retail PS4
    if game.platform == ExcelPlatform.PLAYSTATION_4:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (PSN)"
        return f"{game.platform.value} (Emulation)"

    # Digital / Retail PS5
    if game.platform == ExcelPlatform.PLAYSTATION_5:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (PSN)"
        return f"{game.platform.value} (Emulation)"
    # Digital / Retail Vita
    if game.platform == ExcelPlatform.PLAYSTATION_VITA:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (PSN)"
        return f"{game.platform.value} (Emulation)"

    # Virtual Console
    if game.digital_platform == "Virtual Console":
        return f"{game.platform.value} ({game.digital_platform})"

    # Digital / Retail 3DS
    if game.platform == ExcelPlatform.NINTENDO_3DS:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (eShop)"
        return f"{game.platform.value} (Emulation)"

    # Digital / Retail New 3DS
    if game.platform == ExcelPlatform.NEW_NINTENDO_3DS:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (eShop)"
        return f"{game.platform.value} (Emulation)"

    # Digital / Retail Wii U
    if game.platform == ExcelPlatform.NINTENDO_WII_U:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (eShop)"
        return f"{game.platform.value} (Emulation)"

    # Digital / Retail Switch
    if game.platform == ExcelPlatform.NINTENDO_SWITCH:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (eShop)"
        return f"{game.platform.value} (Emulation)"

    # Any Required Accessory
    if game.required_accessory is not None:
        return f"{game.platform.value} ({game.required_accessory})"

    # Digital / Retail PSP
    if game.platform == ExcelPlatform.PLAYSTATION_PORTABLE:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value} (PSN)"
        return f"{game.platform.value} (Emulation)"

    if not game.owned and game.platform not in (
        ExcelPlatform.PC,
        ExcelPlatform.BROWSER,
    ):
        return f"{game.platform.value} (Emulation)"

    return game.platform.value


def get_alphabetical_first_letter(game: ExcelGame) -> str:
    return (
        game.normal_title[0].capitalize()
        if game.normal_title[0].isalpha()
        else "#" if game.normal_title[0].isdigit() else "?"
    )


def one_per_criteria_challenge(
    games: List[ExcelGame],
    data_provider: DataProvider,
    grouping: Callable[[ExcelGame], Any],
) -> List[ExcelGame]:
    remaining: List[ExcelGame] = []
    grouped = GameGrouping(grouping).get_groups(games)

    completed = set(
        grouping(cg)
        for cg in filter(
            lambda cg: cg.date_completed is not None
            and cg.date_completed.date() > CHALLENGE_START.date(),
            data_provider.get_played_games(),
        )
    )

    for item, group in grouped.items():
        if item in completed:
            continue
        remaining.extend([pg.game for pg in group])

    return remaining


def get_one_per_criteria_challenge_selector(
    criteria_name: str,
    data_provider: DataProvider,
    grouping: Callable[[ExcelGame], Any],
    games_override: Optional[List[ExcelGame]] = None,
    challenge_suffix: str = "",
    completions: bool = False,
) -> GameSelector:
    name = f"One Per {criteria_name.title()} Challenge"

    if any(challenge_suffix):
        name += f" {challenge_suffix}"

    if completions:
        name += " Completions"

    def select(games: List[ExcelGame]) -> List[ExcelGame]:
        if completions:
            return list(
                cg
                for cg in filter(
                    lambda cg: cg.date_completed is not None
                    and cg.date_completed.date() > CHALLENGE_START.date(),
                    games,
                )
            )

        return one_per_criteria_challenge(games, data_provider, grouping)

    def get_description(groups: GameGroups) -> str:
        return (
            f"**{len(groups)} {criteria_name.title()}s Remaining to Complete**"
            f"\nPick one game per {criteria_name.lower()}, five options shown."
        )

    return GameSelector(
        select,
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
        grouping=GameGrouping(
            grouping, take=5 if not completions else 1, should_rank=not completions
        ),
        include_platform=criteria_name != "Platform",
        get_description=get_description if not completions else None,
        sort=lambda g: g.game.combined_rating,
        reverse_sort=True,
        name=name,
        games=games_override,
    )
