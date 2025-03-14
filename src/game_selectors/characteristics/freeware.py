from game_selector import GameSelector
from picker_enums import PickerMode

FREEWARE = GameSelector(
    _filter=lambda game: game.notes is not None and game.notes.strip() == "Freeware",
    include_in_picks=False,
    name="Freeware",
    run_on_modes=set([PickerMode.ALL]),
)
