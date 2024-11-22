from typing import Any, List, Tuple
import statistics

from excel_game import ExcelGame
from game_grouping import GameGrouping, GameGroups
from game_selector import GameSelector
from picked_game import PickedGame


def best_companies_by_metacritic(games: List[ExcelGame]) -> List[ExcelGame]:
    by_developer = GameGrouping(lambda g: g.developer).get_groups(
        list(filter(lambda g: g.metacritic_rating is not None, games)),
    )

    by_publisher = GameGrouping(lambda g: g.publisher).get_groups(
        list(filter(lambda g: g.metacritic_rating is not None, games)),
    )

    combined = list(by_developer.items())
    combined.extend(by_publisher.items())

    by_company = {}

    for key, value in combined:
        if key in by_company:
            by_company[key] = by_company[key].union(set(value))
        else:
            by_company[key] = set(value)

    companies_to_remove = []

    for key, value in by_company.items():
        if len(value) < 5:
            companies_to_remove.append(key)

    for company in companies_to_remove:
        del by_company[company]

    company_ratings = GameGroups(by_company).with_agg(
        lambda gs: statistics.mean([g.game.metacritic_rating for g in gs]),
        inplace=False,
    )

    return list(
        set(
            g.game.get_copy_with_metadata(kvp[0])
            for kvp in sorted(
                company_ratings.items(), key=lambda kvp: kvp[1], reverse=True
            )[:10]
            for g in by_company[kvp[0]]
        )
    )


def get_group_name(kvp: Tuple[Any, List[PickedGame]]) -> str:
    mean_rating = statistics.mean(g.game.metacritic_rating for g in kvp[1])

    return f"{kvp[0]} ({len(kvp[1])}) [{mean_rating:.0%}]"


BEST_COMPANIES_BY_METACRITIC = GameSelector(
    best_companies_by_metacritic,
    grouping=GameGrouping(
        lambda g: g.group_metadata,
        reverse=True,
        sort=lambda kvp: (
            statistics.mean(g.game.metacritic_rating for g in kvp[1]),
            kvp[0],
        ),
        get_group_name=get_group_name,
    ),
    sort=lambda g: (g.game.metacritic_rating, g.game.normal_title),
    reverse_sort=True,
    custom_suffix=lambda g: f" - {g.metacritic_rating:.0%}",
    include_in_picks=False,
)
