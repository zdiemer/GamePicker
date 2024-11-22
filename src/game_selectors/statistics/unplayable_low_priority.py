from excel_game import Playability

from data_provider import DataProvider
from excel_filter import ExcelFilter
from game_selector import GameSelector
from picker_enums import PickerMode


def get_unplayable_low_priority_selector(
    data_provider: DataProvider, mode: PickerMode
) -> GameSelector:
    return GameSelector(
        lambda _: list(
            filter(
                lambda g: g.playability != Playability.PLAYABLE
                and not g.completed
                and g.priority <= 2
                and ExcelFilter.included_in_mode(g, mode),
                data_provider.get_games(),
            )
        ),
        name="Unplayable Low Priority",
        include_in_picks=False,
        run_on_modes=set([PickerMode.ALL]),
    )
