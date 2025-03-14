import datetime

from excel_game import FuzzyDateType
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode

ALL_GAMES = GameSelector(
    name="All Games",
    sort=lambda pg: pg.game.release_date,
    reverse_sort=True,
    custom_prefix=lambda g: (
        datetime.datetime.strftime(g.release_date, "%b %d: ")
        if g.fuzzy_date is None
        else (
            datetime.datetime.strftime(g.release_date, "%b: ")
            if g.fuzzy_date == FuzzyDateType.MONTH_AND_YEAR_ONLY
            else ""
        )
    ),
    grouping=GameGrouping(
        lambda g: g.release_year,
        reverse=True,
    ),
    run_on_modes=set([PickerMode.ALL]),
)
