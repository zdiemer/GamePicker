from typing import List
import copy

from excel_game import ExcelGame
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def backloggd_top(
    games: List[ExcelGame], data_provider: DataProvider
) -> List[ExcelGame]:
    pop_iter = data_provider.backloggd_client.get_popular_games()
    validator = data_provider.get_validator()

    popular = []
    i = 0
    pi = 0

    for g in pop_iter:
        upg = next(
            filter(
                lambda _g: validator.titles_equal_normalized(g, _g.title),
                games,
            ),
            None,
        )

        if upg is not None:
            upgc = copy.copy(upg)
            upgc.group_metadata = i
            popular.append(upgc)
            i += 1

        if len(popular) >= 50 or (pi / 50) > 10:
            break

    return popular


def get_backloggd_top_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        lambda games: backloggd_top(games, data_provider),
        grouping=GameGrouping(lambda _: "Trending"),
        sort=lambda g: g.game.group_metadata,
        custom_prefix=lambda g: f"{g.group_metadata + 1}. ",
        skip_unless_specified=True,
        no_force=True,
        name="Backloggd Top",
        run_on_modes=set([PickerMode.ALL]),
    )
