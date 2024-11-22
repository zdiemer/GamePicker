from excel_game import TranslationStatus

from data_provider import DataProvider
from game_selector import GameSelector
from picker_enums import PickerMode


def get_untranslated_games_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        name="Untranslated Games",
        _filter=lambda g: not g.completed and g.translation == TranslationStatus.NONE,
        games=data_provider.get_games(),
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
    )
