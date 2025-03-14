from excel_game import ExcelOwnedFormat
from game_selector import GameSelector
from picker_enums import PickerMode

PHYSICAL_GAMES = GameSelector(
    _filter=lambda game: game.owned_format
    in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL),
    name="Physical Games",
)
