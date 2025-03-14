import statistics
from game_selector import GameSelector

UNDERPRIORITIZED = GameSelector(
    _filter=lambda g: (g.metacritic_rating is not None or g.gamefaqs_rating is not None)
    and (g.priority / 5) * (1 + (1 / 3))
    < statistics.mean(
        list(filter(lambda r: r is not None, [g.metacritic_rating, g.gamefaqs_rating]))
    ),
    name="Underprioritized",
)
