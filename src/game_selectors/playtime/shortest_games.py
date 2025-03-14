from typing import Any, Callable

from excel_game import ExcelGame, ExcelGenre

from game_grouping import GameGrouping
from game_selector import GameSelector

SHORTEST_GAMES = GameSelector(
    _filter=lambda g: g.estimated_playtime is not None,
    sort=lambda g: g.game.estimated_playtime,
    name="Shortest Games",
    include_platform=False,
    grouping=GameGrouping(group_size=10),
)

SHORTEST_OVERALL = GameSelector(
    _filter=lambda g: g.estimated_playtime is not None,
    sort=lambda g: g.game.estimated_playtime,
    name="Shortest Overall",
    grouping=GameGrouping(lambda _: "Shortest", group_size=100),
)

SHORTEST_OVERALL_UNCOMMON_GENRE = GameSelector(
    _filter=lambda game: game.estimated_playtime is not None
    and game.genre not in (ExcelGenre.FIGHTING, ExcelGenre.SCROLLING_SHOOTER),
    sort=lambda g: g.game.estimated_playtime,
    name="Shortest Overall - Uncommon Genre",
    grouping=GameGrouping(lambda _: "Shortest", group_size=100),
)


def get_shortest_by_selector(
    grouping: Callable[[ExcelGame], Any], name: str
) -> GameSelector:
    return GameSelector(
        _filter=lambda g: g.estimated_playtime is not None,
        sort=lambda g: g.game.estimated_playtime,
        name=name,
        grouping=GameGrouping(grouping, group_size=10),
    )
