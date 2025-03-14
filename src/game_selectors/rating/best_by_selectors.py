from typing import Any, Callable, Optional

from excel_game import ExcelGame
from game_grouping import GameGrouping
from game_selector import GameSelector


def get_best_by_selector(
    grouping: Optional[Callable[[ExcelGame], Any]],
    name: str,
    reverse_grouping_sort: bool = False,
) -> GameSelector:
    return GameSelector(
        custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
        sort=lambda g: g.game.combined_rating,
        reverse_sort=True,
        name=name,
        grouping=GameGrouping(grouping, reverse=reverse_grouping_sort, group_size=10),
        include_platform=grouping is not None,
    )
