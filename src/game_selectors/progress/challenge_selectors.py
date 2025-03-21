from typing import Any, Callable, List, Optional, Set, Tuple
import datetime

from excel_game import ExcelGame, ExcelOwnedFormat, ExcelPlatform, ExcelRegion
from data_provider import DataProvider
from game_grouping import GameGrouping, GameGroups
from game_selector import GameSelector
from picked_game import PickedGame
from picker_enums import PickerMode

CHALLENGE_START: datetime.datetime = datetime.datetime(2024, 10, 20)


def get_platform_completion_id(game: ExcelGame) -> str:
    # One Per PC / Playdate Subplatform
    if game.digital_platform is not None:
        vr = " (VR)" if game.vr else ""
        dlc = " (DLC)" if game.dlc else ""
        return f"{game.platform.value} ({game.digital_platform}){vr}{dlc}"

    # DLC
    if game.dlc:
        return f"{game.platform.value} (DLC)"

    # MAME and Non-Mame
    if game.platform == ExcelPlatform.ARCADE:
        if game.physical_media_format == "LaserDisc":
            return f"{game.platform.value} (LaserDisc)"
        if game.notes in ("Atomiswave", "Naomi"):
            return f"{game.platform.value} (Naomi)"
        if game.notes == "Triforce":
            return f"{game.platform.value} (Triforce)"
        if game.notes == "Chihiro":
            return f"{game.platform.value} (Chihiro)"
        if game.notes == "System 573":
            return f"{game.platform.value} (System 573)"
        if game.mame_romset is not None:
            return f"{game.platform.value} (MAME)"
        return f"{game.platform.value} (Non-MAME)"

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
        vr_str = " (VR)" if game.vr else ""
        return f"{game.platform.value}{vr_str} ({game.subscription_service})"

    # Digital / Retail Xbox 360 / XBLIG
    if game.platform == ExcelPlatform.XBOX_360:
        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value} ({game.release_region.value} Retail)"
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
        vr_str = " (VR)" if game.vr else ""

        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value}{vr_str} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value}{vr_str} (PSN)"
        return f"{game.platform.value}{vr_str} (Emulation)"

    # Digital / Retail PS5
    if game.platform == ExcelPlatform.PLAYSTATION_5:
        vr_str = " (VR)" if game.vr else ""

        if game.owned_format in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL):
            return f"{game.platform.value}{vr_str} ({game.release_region.value} Retail)"
        if game.owned_format == ExcelOwnedFormat.DIGITAL:
            return f"{game.platform.value}{vr_str} (PSN)"
        return f"{game.platform.value}{vr_str} (Emulation)"
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


def __get_playtime_str(playtime: Optional[float]) -> str:
    if playtime is None:
        return "No Playtime"

    if playtime < 1:
        return "Under 1 Hour"

    playtime = int(playtime)

    return f"{playtime} Hour{'s' if playtime != 1 else ''}"


def get_playtime(game: ExcelGame) -> str:
    if game.completed:
        return __get_playtime_str(game.completion_time)

    return __get_playtime_str(game.estimated_playtime)


def get_top_developers(games: List[ExcelGame], n: int = 50) -> Set[str]:
    developer_counts = (
        GameGrouping(lambda g: g.developer).get_groups(games).with_agg(len)
    )

    return set(
        list(
            kvp[0]
            for kvp in sorted(
                developer_counts.items(), key=lambda kvp: kvp[1], reverse=True
            )
        )[:n]
    )


def one_per_criteria_challenge(
    games: List[ExcelGame],
    data_provider: DataProvider,
    grouping: Callable[[ExcelGame], Any],
    challenge_start: datetime.datetime = CHALLENGE_START,
) -> List[ExcelGame]:
    remaining: List[ExcelGame] = []
    grouped = GameGrouping(grouping).get_groups(games)

    completed = set(
        grouping(cg)
        for cg in filter(
            lambda cg: cg.date_completed is not None
            and cg.date_completed.date() > challenge_start.date(),
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
    challenge_start: datetime.datetime = CHALLENGE_START,
    custom_grouping_sort: Optional[
        Callable[[Tuple[Any, List[PickedGame]]], Any]
    ] = None,
    custom_grouping_sort_reverse: bool = False,
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
                    and cg.date_completed.date() > challenge_start.date(),
                    games,
                )
            )

        selected = one_per_criteria_challenge(
            games, data_provider, grouping, challenge_start
        )

        return selected

    def get_description(groups: GameGroups, completions: bool) -> str:
        rem_or_completed = "Remaining to Complete" if not completions else "Completed"
        pick_one = (
            f"\nPick one game per {criteria_name.lower()}, five options shown."
            if not completions
            else ""
        )

        return (
            f"**{len(groups)} {criteria_name.title()}{'s' if len(groups) != 1 else ''}"
            f" {rem_or_completed}**{pick_one}"
        )

    return GameSelector(
        select,
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
        grouping=GameGrouping(
            grouping,
            group_size=5 if not completions else 1,
            should_rank=not completions,
            sort=custom_grouping_sort,
            reverse=custom_grouping_sort_reverse,
        ),
        include_platform=criteria_name != "Platform",
        get_description=lambda groups: get_description(groups, completions),
        sort=lambda g: (
            g.game.combined_rating if not completions else g.game.date_completed
        ),
        reverse_sort=not completions,
        name=name,
        games=games_override,
    )
