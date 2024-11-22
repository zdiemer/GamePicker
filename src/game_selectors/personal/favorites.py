from typing import List
import statistics

from excel_game import ExcelGame
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector


def favorites(games: List[ExcelGame], data_provider: DataProvider) -> List[ExcelGame]:
    played_games = data_provider.get_played_games()

    by_developer = (
        GameGrouping(lambda g: g.developer)
        .get_groups(played_games)
        .with_agg(lambda gs: statistics.mean(g.game.rating for g in gs))
    )

    by_publisher = (
        GameGrouping(lambda g: g.publisher)
        .get_groups(played_games)
        .with_agg(lambda gs: statistics.mean(g.game.rating for g in gs))
    )

    by_franchise = (
        GameGrouping(lambda g: g.franchise)
        .get_groups(list(filter(lambda g: g.franchise is not None, played_games)))
        .with_agg(lambda gs: statistics.mean(g.game.rating for g in gs))
    )

    favorite_developers = set(
        kvp[0]
        for kvp in sorted(by_developer.items(), key=lambda kvp: kvp[1], reverse=True)[
            :10
        ]
    )

    favorite_publishers = set(
        kvp[0]
        for kvp in sorted(by_publisher.items(), key=lambda kvp: kvp[1], reverse=True)[
            :10
        ]
    )

    favorite_franchises = set(
        kvp[0]
        for kvp in sorted(by_franchise.items(), key=lambda kvp: kvp[1], reverse=True)[
            :10
        ]
    )

    unplayed_favorites = set()

    for g in games:
        if g.developer in favorite_developers:
            unplayed_favorites.add(
                g.get_copy_with_metadata(f"Developer: {g.developer}")
            )
        if g.publisher in favorite_publishers:
            unplayed_favorites.add(
                g.get_copy_with_metadata(f"Publisher: {g.publisher}")
            )
        if g.franchise in favorite_franchises:
            unplayed_favorites.add(
                g.get_copy_with_metadata(f"Franchise: {g.franchise}")
            )

    return list(unplayed_favorites)


def get_favorites_selector(data_provider: DataProvider):
    return GameSelector(
        lambda games: favorites(games, data_provider),
        grouping=GameGrouping(
            lambda g: f'{g.group_metadata.split(":")[0]}s',
            subgroupings=[
                GameGrouping(lambda g: g.group_metadata.split(":")[1].strip())
            ],
        ),
        name="Favorites",
    )
