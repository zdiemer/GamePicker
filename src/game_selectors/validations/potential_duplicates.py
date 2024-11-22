from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode

POTENTIAL_DUPLICATES = GameSelector(
    grouping=GameGrouping(lambda g: g.title, _filter=lambda kvp: len(kvp[1]) > 1),
    include_in_picks=False,
    name="Potential Duplicates",
    run_on_modes=set([PickerMode.ALL]),
)
