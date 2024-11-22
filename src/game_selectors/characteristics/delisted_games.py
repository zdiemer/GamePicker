from game_selector import GameSelector
from picker_enums import PickerMode

DELISTED_GAMES = GameSelector(
    _filter=lambda g: g.delisted,
    name="Delisted Games",
    run_on_modes=set([PickerMode.ALL]),
    include_in_picks=False,
)
