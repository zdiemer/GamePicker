from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode

LIMITED_PRINT_GAMES = GameSelector(
    _filter=lambda g: g.limited_print_company is not None,
    name="Limited Print Games",
    grouping=GameGrouping(lambda g: g.limited_print_company),
)
