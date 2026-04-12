from typing import Optional

from data_provider import DataProvider
from excel_game import ExcelGame
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def get_average_daily_playtime(game: ExcelGame) -> Optional[float]:
    if (
        game.date_started is None
        or game.date_completed is None
        or game.completion_time is None
    ):
        return None

    days_played = (game.date_completed - game.date_started).days + 1

    return game.completion_time / days_played


def get_playtime_string(playtime: float) -> str:
    if playtime < 1:
        playtime *= 60
        if playtime < 1:
            return f"{playtime * 60:.2f} seconds"
        return f"{playtime:.2f} minutes"

    return f"{playtime:.2f} hours"


def get_average_playtime_per_day_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        lambda games: list(
            filter(
                lambda _g: _g.group_metadata is not None,
                (
                    g.get_copy_with_metadata(get_average_daily_playtime(g))
                    for g in games
                ),
            )
        ),
        name="Average Playtime Per Day",
        custom_suffix=lambda g: f" - {get_playtime_string(g.group_metadata)}",
        sort=lambda pg: pg.game.group_metadata,
        reverse_sort=True,
        grouping=GameGrouping(lambda _: "Average Playtime Per Day", should_rank=False),
        run_on_modes=set([PickerMode.ALL]),
        games=data_provider.get_played_games(),
    )
