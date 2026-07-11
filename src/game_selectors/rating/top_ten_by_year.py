from datetime import datetime

from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector


def get_top_ten_by_year_selector(
    data_provider: DataProvider,
) -> GameSelector:
    completed_games = data_provider.get_completed_games()

    completed_games_by_year = GameGrouping(lambda g: g.date_completed.year).get_groups(
        list(filter(lambda g: g.date_completed is not None, completed_games))
    )

    completed_games_with_ties = []

    for games in completed_games_by_year.values():
        year_games_by_rating = GameGrouping(lambda g: g.rating).get_groups(
            [g.game for g in games if g.game.rating is not None]
        )

        for _rating, rating_games in sorted(
            year_games_by_rating.items(), key=lambda kvp: kvp[0], reverse=True
        )[:10]:
            if len(rating_games) == 1:
                completed_games_with_ties.append(rating_games[0].game)
            else:
                tied_game = rating_games[0].game.get_copy_with_metadata(
                    " + ".join([g.game.full_name for g in rating_games])
                )
                completed_games_with_ties.append(tied_game)

    return GameSelector(
        custom_suffix=lambda g: (
            f"{g.group_metadata} - {g.rating:.0%}"
            if g.group_metadata is not None
            else f" - {g.rating:.0%}"
        ),
        sort=lambda g: g.game.rating or 0.0,
        reverse_sort=True,
        name="Top Ten by Year",
        grouping=GameGrouping(
            lambda g: g.date_completed.year if g.date_completed else datetime.max,
            reverse=True,
            group_size=10,
        ),
        include_platform=False,
        games=completed_games_with_ties,
    )
