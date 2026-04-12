from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector


def get_next_per_franchise_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        lambda games: list(
            filter(
                lambda g: g.franchise
                in set(_g.franchise for _g in data_provider.get_played_games()),
                games,
            )
        ),
        name="Next Per Franchise",
        grouping=GameGrouping(lambda g: g.franchise, group_size=1),
        sort=lambda pg: pg.game.release_date,
    )
