from typing import Any, Callable, Optional

from excel_game import ExcelGame
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def get_most_played_selector(
    data_provider: DataProvider,
    grouping: Callable[[ExcelGame], Any],
    name: str,
    _filter: Optional[Callable[[ExcelGame], bool]] = None,
) -> GameSelector:
    return GameSelector(
        _filter=_filter,
        name=name,
        grouping=GameGrouping(
            grouping,
            get_group_name=lambda kvp: f"{kvp[0]} ({sum(g.game.completion_time or 0 for g in kvp[1]):,.2f}hr) [{len(kvp[1])}]",
            sort=lambda kvp: sum(g.game.completion_time or 0 for g in kvp[1]),
            reverse=True,
            should_rank=False,
            _filter=lambda kvp: sum(g.game.completion_time or 0 for g in kvp[1]) > 0,
        ),
        include_in_picks=False,
        run_on_modes=set([PickerMode.ALL]),
        games=data_provider.get_played_games(),
        custom_suffix=lambda g: (
            f" [{g.completion_time:,.2f}hr]" if g.completion_time is not None else ""
        ),
        sort=lambda pg: pg.game.completion_time or 0,
        reverse_sort=True,
    )
