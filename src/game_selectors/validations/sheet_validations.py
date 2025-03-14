from typing import List, Set
import copy
import datetime
import re
import statistics

from excel_game import ExcelGame, ExcelOwnedFormat, ExcelPlatform, ExcelRegion
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def sheet_validations(
    games: List[ExcelGame], data_provider: DataProvider
) -> List[ExcelGame]:
    invalid_games: List[ExcelGame] = []
    all_titles: Set[str] = set([])

    for game in games:
        all_titles.add(game.title)

        # Owned Physical Games Missing Condition
        if (
            game.owned
            and game.owned_format in (ExcelOwnedFormat.PHYSICAL, ExcelOwnedFormat.BOTH)
            and game.owned_condition is None
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Missing Condition"
            invalid_games.append(g_copy)

        # Owned Games Missing Format
        if game.owned and (game.owned_format is None or game.owned == ""):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Missing Format"
            invalid_games.append(g_copy)

        # Completed Games with Lingering Metadata
        if game.completed and (
            game.estimated_playtime is not None or game.priority is not None
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Lingering Metadata"
            invalid_games.append(g_copy)

        # Wishlisted and Owned
        if game.owned and game.wishlisted:
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Wishlisted and Owned"
            invalid_games.append(g_copy)

        # Missing Rating
        if game.completed and game.rating is None:
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Missing Rating"
            invalid_games.append(g_copy)

        # Owned PC Game Missing Subplatform
        if (
            game.owned
            and game.platform == ExcelPlatform.PC
            and (game.notes is None or game.notes == "")
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Missing PC Subplatform"
            invalid_games.append(g_copy)

        # Unowned With Ownership Metadata
        if not game.owned and (
            game.owned_condition is not None
            or (game.date_purchased is not None and game.date_purchased != "")
            or (game.purchase_price is not None and game.purchase_price != "")
            or (game.owned_format is not None and game.owned_format != "")
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Unowned With Ownership Metadata"
            invalid_games.append(g_copy)

        # Browser Based Games Without Links
        if (
            not game.completed
            and game.platform == ExcelPlatform.BROWSER
            and game.notes
            not in (
                "Link",
                "itch.io",
            )
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Browser Games Without Links"
            invalid_games.append(g_copy)

        # Missing Translation Info
        if (
            game.release_region
            not in (
                ExcelRegion.EUROPE,
                ExcelRegion.NORTH_AMERICA,
                ExcelRegion.AUSTRALIA,
            )
            and game.translation is None
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Missing Translation Info"
            invalid_games.append(g_copy)

        # Estimated Time Not Multiple of 0.5
        if (
            game.estimated_playtime is not None
            and game.estimated_playtime > 1
            and game.estimated_playtime != 0.5 * round(game.estimated_playtime / 0.5)
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Estimated Playtime Using Incorrect Multiple"
            invalid_games.append(g_copy)

        # Trailing Whitespace
        if (
            game.title != game.title.strip()
            or game.publisher != game.publisher.strip()
            or game.developer != game.developer.strip()
            or (game.franchise is not None and game.franchise != game.franchise.strip())
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Trailing Whitespace"
            invalid_games.append(g_copy)

        double_space_re = r"[ ]{2,}"

        # Double Spaces
        if (
            re.search(double_space_re, game.title) is not None
            or re.search(double_space_re, game.publisher) is not None
            or re.search(double_space_re, game.developer) is not None
            or (
                game.franchise is not None
                and re.search(double_space_re, game.franchise) is not None
            )
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Double Spaces"
            invalid_games.append(g_copy)

        # Start Date After Completed Date
        if (
            game.date_started is not None
            and game.date_completed is not None
            and game.date_started > game.date_completed
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Start Date After Completed Date"
            invalid_games.append(g_copy)

    games_dict = {g.hash_id: g for g in data_provider.get_games()}

    def round_to_2(num: float) -> float:
        return float(f"{num:,.2f}")

    def to_percent(num: float) -> int:
        return round(num * 100)

    for cur, game in enumerate(
        sorted(
            data_provider.get_completed_games(),
            key=lambda g: g.completion_number,
        )
    ):
        # Collection Title Missing from Main Sheet
        if (
            game.collection is not None
            and game.collection != ""
            and game.collection not in all_titles
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Completed: Collection Mismatch"
            invalid_games.append(g_copy)

        # Typo in Notes
        if game.notes is not None and game.notes != "":
            pass

        # Incorrect Completion Number
        if game.completion_number != cur + 1:
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Completed: Completion Number Incorrect"
            invalid_games.append(g_copy)

        if game.hash_id in games_dict:
            # Rating Mismatch
            if to_percent(game.rating) != to_percent(
                games_dict[game.hash_id].rating or 0
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Completed: Rating Mismatch"
                invalid_games.append(g_copy)

            # Playtime Mismatch
            if round_to_2(game.completion_time or 0) != round_to_2(
                games_dict[game.hash_id].completion_time or 0
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Completed: Completion Time Mismatch"
                invalid_games.append(g_copy)

            # Completed Date Mismatch
            if game.date_completed != games_dict[game.hash_id].date_completed:
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Completed: Completed Date Mismatch"
                invalid_games.append(g_copy)

            # Started Date Mismatch
            if game.date_started != games_dict[game.hash_id].date_started:
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Completed: Completed Start Date Mismatch"
                invalid_games.append(g_copy)

            # Missing VR Metadata
            if game.played_in_vr and not games_dict[game.hash_id].vr:
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Completed: VR Metadata Mismatch"
                invalid_games.append(g_copy)

    order_hash_dict = {g.game_order_hash_id: g for g in data_provider.get_games()}

    for game in data_provider.get_games_on_order():
        # Estimated Release Passed
        if (
            game.estimated_release is not None
            and game.estimated_release.date() < datetime.datetime.now().date()
        ):
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Games on Order: Past Estimated Release"
            invalid_games.append(g_copy)

        # Games Added to Main Sheet but Not Removed from Games on Order
        if game.game_order_hash_id in order_hash_dict:
            g_copy = copy.copy(game)
            g_copy.group_metadata = "Games on Order: Not Removed From Order Sheet"
            invalid_games.append(g_copy)

    merged_games, errors = data_provider.get_excel_loader().merge()

    for error in errors:
        e_game, msg = error
        g_copy = copy.copy(e_game)
        g_copy.group_metadata = msg
        invalid_games.append(g_copy)

    for game in merged_games:
        if any(game.child_games) and game.hash_id in games_dict:
            # Collection's Total Playtime Doesn't Match Individual Entries
            if round_to_2(sum(g.completion_time or 0 for g in game.child_games)) > (
                round_to_2(games_dict[game.hash_id].completion_time or 0)
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Completed: Collection Completion Time Mismatch"
                invalid_games.append(g_copy)

            # Collection's Rating Doesn't Match Individual Entries' Average
            if to_percent(
                statistics.mean(g.rating for g in game.child_games)
            ) != to_percent(games_dict[game.hash_id].rating or 0):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Completed: Collection Rating Mismatch"
                invalid_games.append(g_copy)

            # Collection's Completed Date Doesn't Match Individual Entries' Max
            if (
                games_dict[game.hash_id].completed
                and any(
                    filter(lambda g: g.date_completed is not None, game.child_games)
                )
                and games_dict[game.hash_id].date_completed
                != max(
                    g.date_completed
                    for g in filter(
                        lambda _g: _g.date_completed is not None, game.child_games
                    )
                )
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Completed: Collection Completed Date Mismatch"
                invalid_games.append(g_copy)

    return invalid_games


def get_sheet_validations_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        lambda games: sheet_validations(games, data_provider),
        games=data_provider.get_games(),
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
        grouping=GameGrouping(lambda g: g.group_metadata, should_rank=False),
        name="Sheet Validations",
    )
