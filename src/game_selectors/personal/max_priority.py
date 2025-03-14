from game_selector import GameSelector

MAX_PRIORITY = GameSelector(
    _filter=lambda g: g.priority == 5,
    name="Max Priority",
)
