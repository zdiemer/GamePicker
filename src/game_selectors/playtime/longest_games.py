from game_grouping import GameGrouping
from game_selector import GameSelector

LONGEST_GAMES = GameSelector(
    _filter=lambda g: g.estimated_playtime is not None,
    sort=lambda g: g.game.estimated_playtime,
    reverse_sort=True,
    include_platform=False,
    name="Longest Games",
    grouping=GameGrouping(take=10),
)
