from game_selector import GameSelector
from picker_enums import PickerMode

VIRTUAL_CONSOLE = GameSelector(
    _filter=lambda g: g.digital_platform == "Virtual Console",
    name="Virtual Console",
    run_on_modes=set([PickerMode.ALL]),
)
