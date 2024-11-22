from data_provider import DataProvider
from excel_filter import ExcelFilter
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def get_now_playing_selector(
    data_provider: DataProvider, mode: PickerMode
) -> GameSelector:
    return GameSelector(
        lambda _: list(
            filter(
                lambda g: ExcelFilter.included_in_mode(g, mode)
                and g.playing_status is not None,
                data_provider.get_games(),
            )
        ),
        grouping=GameGrouping(
            lambda g: g.playing_status.name.replace("_", " ").title(),
            subgroupings=[GameGrouping(should_rank=False)],
            should_rank=False,
        ),
        name="Now Playing",
        include_in_picks=False,
        include_platform=False,
        run_on_modes=set([PickerMode.ALL]),
        custom_suffix=lambda g: (
            f" - {g.playing_progress:.0%} complete"
            if g.playing_progress is not None
            else ""
        ),
        sort=lambda pg: pg.game.playing_progress or 0,
        reverse_sort=True,
    )
