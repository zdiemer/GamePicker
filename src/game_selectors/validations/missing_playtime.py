from excel_game import ExcelPlatform

from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def get_missing_playtime_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        _filter=lambda g: g.completion_time is None
        and not g.emulated
        and (
            g.platform
            in (
                ExcelPlatform.NINTENDO_3DS,
                ExcelPlatform.NINTENDO_SWITCH,
                ExcelPlatform.PLAYSTATION_4,
                ExcelPlatform.PLAYSTATION_5,
                ExcelPlatform.XBOX_ONE,
                ExcelPlatform.XBOX_SERIES_X_S,
            )
            or g.digital_platform == "Steam"
        ),
        run_on_modes=set([PickerMode.ALL]),
        games=data_provider.get_completed_games(),
        include_in_picks=False,
        include_platform=False,
        grouping=GameGrouping(should_rank=False),
        name="Missing Playtime",
    )
