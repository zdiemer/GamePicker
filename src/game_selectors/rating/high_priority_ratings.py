import statistics
from game_selector import GameSelector
from picker_enums import PickerMode

HIGH_PRIORITY_RATINGS = GameSelector(
    _filter=lambda g: (g.metacritic_rating is not None or g.gamefaqs_rating is not None)
    and (g.priority / 5)
    >= (
        statistics.mean(
            list(
                filter(
                    lambda r: r is not None, [g.metacritic_rating, g.gamefaqs_rating]
                )
            )
        )
    )
    * 1.5,
    name="High Priority Ratings",
    sort=lambda g: g.game.combined_rating,
    reverse_sort=True,
    run_on_modes=set([PickerMode.ALL]),
)
