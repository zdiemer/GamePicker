from typing import List

from excel_game import ExcelGame
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector


def zero_percent(
    games: List[ExcelGame], data_provider: DataProvider
) -> List[ExcelGame]:
    by_platform = GameGrouping().get_groups(data_provider.get_played_games())
    by_genre = GameGrouping(lambda g: g.genre).get_groups(
        data_provider.get_played_games()
    )
    by_metacritic = GameGrouping(
        lambda g: f"{(g.metacritic_rating * 100) // 10 / 10:.0%}"
    ).get_groups(
        list(
            filter(
                lambda g: g.metacritic_rating is not None,
                data_provider.get_played_games(),
            )
        ),
    )
    by_game_faqs = GameGrouping(
        lambda g: f"{(g.gamefaqs_rating * 100) // 10 / 10:.0%}"
    ).get_groups(
        list(
            filter(
                lambda g: g.gamefaqs_rating is not None,
                data_provider.get_played_games(),
            )
        ),
    )
    by_year = GameGrouping(lambda g: g.release_year).get_groups(
        data_provider.get_played_games(),
    )

    zeroes = []

    for game in games:
        if game.platform not in by_platform:
            zeroes.append(game.get_copy_with_metadata(f"Platform: {game.platform}"))
        if game.genre not in by_genre:
            zeroes.append(game.get_copy_with_metadata(f"Genre: {game.genre}"))
        if (
            game.metacritic_rating is not None
            and f"{(game.metacritic_rating * 100) // 10 / 10:.0%}" not in by_metacritic
        ):
            zeroes.append(
                game.get_copy_with_metadata(
                    f"Metacritic Rating: {(game.metacritic_rating * 100) // 10 / 10:.0%}",
                )
            )
        if (
            game.gamefaqs_rating is not None
            and f"{(game.gamefaqs_rating * 100) // 10 / 10:.0%}" not in by_game_faqs
        ):
            zeroes.append(
                game.get_copy_with_metadata(
                    f"GameFAQs Rating: {(game.gamefaqs_rating * 100) // 10 / 10:.0%}",
                )
            )
        if game.release_year not in by_year:
            zeroes.append(
                game.get_copy_with_metadata(f"Release Year: {game.release_year}")
            )

    return zeroes


def get_zero_percent_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        lambda games: zero_percent(games, data_provider),
        grouping=GameGrouping(
            lambda g: f'{g.group_metadata.split(":")[0]}s',
            subgroupings=[
                GameGrouping(lambda g: g.group_metadata.split(":")[1].strip())
            ],
        ),
        name="Zero Percent",
    )
