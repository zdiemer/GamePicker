from game_selector import GameSelector
from picker_enums import PickerMode

HIGH_CRITIC_RATINGS = GameSelector(
    _filter=lambda g: g.metacritic_rating is not None
    and g.gamefaqs_rating is not None
    and g.metacritic_rating >= g.gamefaqs_rating * 1.5,
    name="High Critic Ratings",
    sort=lambda g: g.game.combined_rating,
    reverse_sort=True,
    run_on_modes=set([PickerMode.ALL]),
)
