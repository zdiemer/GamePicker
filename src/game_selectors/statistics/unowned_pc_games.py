from excel_game import ExcelPlatform
from data_provider import DataProvider
from excel_filter import ExcelFilter
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def get_unowned_pc_games_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        lambda _: list(
            filter(
                lambda g: ExcelFilter.is_not_low_priority(g)
                and ExcelFilter.is_playable_by_language(g)
                and ExcelFilter.is_released(g)
                and ExcelFilter.is_unplayed(g)
                and g.platform == ExcelPlatform.PC
                and not g.owned
                and g.notes != "Freeware",
                data_provider.get_games(),
            )
        ),
        name="Unowned PC Games",
        include_platform=False,
        grouping=GameGrouping(
            lambda g: g.playability.name.title(),
            subgroupings=[GameGrouping(lambda g: g.release_year)],
        ),
        run_on_modes=set([PickerMode.ALL]),
    )
