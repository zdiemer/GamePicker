from typing import NamedTuple, Optional

from game_selector import GameSelector


class PlaytimeBounds(NamedTuple):
    lower: Optional[int]
    upper: Optional[int]


def get_playtime_selector(name: str, bounds: PlaytimeBounds):
    return GameSelector(
        _filter=lambda game: game.estimated_playtime is not None
        and (bounds.lower or float("-inf"))
        <= game.estimated_playtime
        < (bounds.upper or float("inf")),
        name=name,
    )


NO_ESTIMATED_PLAYTIME = GameSelector(
    _filter=lambda g: g.estimated_playtime is None,
    name="No Estimated Playtime",
)
