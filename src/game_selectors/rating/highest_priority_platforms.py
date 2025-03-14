import statistics

from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


HIGHEST_PRIORITY_PLATFORMS = GameSelector(
    name="Highest Priority Platforms",
    grouping=GameGrouping(
        get_group_name=lambda kvp: f"{kvp[0]} ({statistics.mean(g.game.priority for g in kvp[1]):,.2f}) [{len(kvp[1])}]",
        sort=lambda kvp: statistics.mean(g.game.priority for g in kvp[1]),
        reverse=True,
    ),
    include_in_picks=False,
    run_on_modes=set([PickerMode.ALL]),
)
