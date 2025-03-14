from excel_game import TranslationStatus
from game_selector import GameSelector
from picker_enums import PickerMode


FAN_TRANSLATIONS = GameSelector(
    _filter=lambda g: g.translation == TranslationStatus.COMPLETE and not g.owned,
    name="Fan Translations",
)
