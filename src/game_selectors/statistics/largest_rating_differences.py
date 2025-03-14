import statistics

from excel_game import ExcelGame
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def get_custom_suffix(g: ExcelGame) -> str:
    ratings = list(
        filter(lambda r: r is not None, [g.metacritic_rating, g.gamefaqs_rating])
    )

    mean_rating = statistics.mean(ratings)

    rating_difference = g.rating - mean_rating

    return (
        f"\n        - Difference: {rating_difference:+.2%}"
        f"\n        - Average: {mean_rating:.2%}"
        f"\n        - Personal: {g.rating:.2%}\n"
    )


def get_largest_rating_differences_selector(
    data_provider: DataProvider,
) -> GameSelector:
    return GameSelector(
        lambda _: list(
            filter(
                lambda g: (
                    g.metacritic_rating is not None or g.gamefaqs_rating is not None
                ),
                data_provider.get_played_games(),
            )
        ),
        name="Largest Rating Differences",
        sort=lambda g: abs(
            g.game.rating
            - statistics.mean(
                list(
                    filter(
                        lambda r: r is not None,
                        [g.game.metacritic_rating, g.game.gamefaqs_rating],
                    )
                )
            )
        ),
        reverse_sort=True,
        custom_suffix=get_custom_suffix,
        grouping=GameGrouping(
            lambda _: "Largest Rating Differences",
            group_size=100,
            should_rank=False,
        ),
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
    )
