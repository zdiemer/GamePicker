from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector


def get_major_indie_games_selector(data_provider: DataProvider):
    return GameSelector(
        _filter=lambda g: (
            (g.metacritic_rating and g.metacritic_rating >= 0.8)
            or (g.gamefaqs_rating and g.gamefaqs_rating >= 0.8)
        )
        and g.priority > 3
        and g.release_year >= 2009,
        grouping=GameGrouping(
            lambda g: g.developer,
            _filter=lambda kvp: len(kvp[1]) / len(data_provider.get_games()) < 0.0005
            and any(pg.game.publisher == kvp[0] for pg in kvp[1]),
        ),
        name="Major Indie Games",
    )
