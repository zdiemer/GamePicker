from excel_game import ExcelGenre
from game_grouping import GameGrouping
from game_selector import GameSelector

UNDER_1_HOUR_UNCOMMON_GENRE = GameSelector(
    _filter=lambda game: game.estimated_playtime is not None
    and game.estimated_playtime < 1
    and game.genre not in (ExcelGenre.FIGHTING, ExcelGenre.SCROLLING_SHOOTER),
    name="Under 1 Hour - Uncommon Genre",
    grouping=GameGrouping(lambda g: g.genre),
)
