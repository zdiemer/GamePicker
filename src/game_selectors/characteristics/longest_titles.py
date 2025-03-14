from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode

LONGEST_TITLES = GameSelector(
    name="Longest Titles",
    sort=lambda pg: len(pg.game.title),
    reverse_sort=True,
    grouping=GameGrouping(lambda _: "Longest Titles", group_size=50),
    include_in_picks=False,
)
