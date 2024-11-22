from typing import Any, List, Tuple
import statistics

from excel_game import ExcelGame
from game_grouping import GameGrouping
from game_selector import GameSelector
from picked_game import PickedGame


def best_years_by_metacritic(games: List[ExcelGame]) -> List[ExcelGame]:
    by_year = GameGrouping(lambda g: g.release_year).get_groups(
        list(filter(lambda g: g.metacritic_rating is not None, games)),
    )

    years_to_remove = []

    for key, value in by_year.items():
        if len(value) < 5:
            years_to_remove.append(key)

    for year in years_to_remove:
        del by_year[year]

    year_ratings = by_year.with_agg(
        lambda gs: statistics.mean([g.game.metacritic_rating for g in gs]),
        inplace=False,
    )

    return [
        g.game
        for kvp in sorted(year_ratings.items(), key=lambda kvp: kvp[1], reverse=True)[
            :10
        ]
        for g in by_year[kvp[0]]
    ]


def get_group_name(kvp: Tuple[Any, List[PickedGame]]) -> str:
    mean_rating = statistics.mean(g.game.metacritic_rating for g in kvp[1])

    return f"{kvp[0]} ({len(kvp[1])}) [{mean_rating:.0%}]"


BEST_YEARS_BY_METACRITIC = GameSelector(
    best_years_by_metacritic,
    grouping=GameGrouping(
        lambda g: g.release_year,
        reverse=True,
        sort=lambda kvp: statistics.mean(g.game.metacritic_rating for g in kvp[1]),
        get_group_name=get_group_name,
    ),
    sort=lambda g: g.game.metacritic_rating,
    reverse_sort=True,
    custom_suffix=lambda g: f" - {g.metacritic_rating:.0%}",
    include_in_picks=False,
)
