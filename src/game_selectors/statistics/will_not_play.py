from data_provider import DataProvider
from game_selector import GameSelector
from picker_enums import PickerMode


def get_will_not_play_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        _filter=lambda g: g.priority == 1,
        run_on_modes=set([PickerMode.ALL]),
        games=data_provider.get_games(),
        include_in_picks=False,
        name="Will Not Play",
    )
