from excel_game import ExcelPlatform
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode

NON_STEAM = GameSelector(
    _filter=lambda g: g.platform == ExcelPlatform.PC
    and g.owned
    and g.digital_platform is not None
    and g.digital_platform != "Steam",
    name="Non-Steam",
    grouping=GameGrouping(lambda g: g.notes),
    include_platform=False,
    include_in_picks=False,
    run_on_modes=set([PickerMode.ALL]),
)
