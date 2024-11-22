from datetime import datetime, timedelta

from excel_game import ExcelGame
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def get_custom_suffix(game: ExcelGame) -> str:
    purchase_or_release = (
        game.date_purchased
        if game.date_purchased >= game.release_date
        else game.release_date
    )

    completion_or_release: datetime = max(game.date_completed, game.release_date)
    time_diff: timedelta = completion_or_release - purchase_or_release

    return (
        f" - {time_diff.days:,} days, "
        f"{time_diff.days / 365:,.1f} years "
        f"(Purchase: {purchase_or_release.strftime('%m/%d/%Y')}, "
        f"Completion: {completion_or_release.strftime('%m/%d/%Y')})"
    )


def get_purchase_to_completion_gaps_selector(
    data_provider: DataProvider,
) -> GameSelector:
    return GameSelector(
        lambda _: list(
            filter(
                lambda g: g.date_purchased is not None and g.date_completed is not None,
                data_provider.get_played_games(),
            )
        ),
        name="Purchase to Completion Gaps",
        sort=lambda g: max(g.game.date_completed, g.game.release_date)
        - (
            g.game.date_purchased
            if g.game.date_purchased >= g.game.release_date
            else g.game.release_date
        ),
        reverse_sort=True,
        custom_suffix=get_custom_suffix,
        grouping=GameGrouping(
            lambda _: "Time Between Purchase", take=100, should_rank=False
        ),
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
    )
