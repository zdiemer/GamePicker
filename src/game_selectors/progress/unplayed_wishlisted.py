from data_provider import DataProvider
from game_selector import GameSelector
from picker_enums import PickerMode


def get_unplayed_wishlisted_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        name="Unplayed Wishlisted",
        run_on_modes=set([PickerMode.ALL]),
        games=list(
            filter(
                lambda g: not g.completed and g.wishlisted,
                data_provider.get_games(),
            )
        ),
        include_in_picks=False,
    )
