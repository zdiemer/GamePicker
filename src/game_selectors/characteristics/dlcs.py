from game_selector import GameSelector
from picker_enums import PickerMode

DLCS = GameSelector(
    _filter=lambda game: game.dlc,
    name="DLCs",
)
