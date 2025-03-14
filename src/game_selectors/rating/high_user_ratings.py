from game_selector import GameSelector
from picker_enums import PickerMode

HIGH_USER_RATINGS = GameSelector(
    _filter=lambda g: g.metacritic_rating is not None
    and g.gamefaqs_rating is not None
    and g.gamefaqs_rating >= g.metacritic_rating * 1.5,
    name="High User Ratings",
    sort=lambda g: g.game.combined_rating,
    reverse_sort=True,
    run_on_modes=set([PickerMode.ALL]),
)
