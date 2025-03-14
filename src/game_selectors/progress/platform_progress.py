from typing import Dict, List, Tuple

from excel_game import ExcelGame, ExcelPlatform
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picked_game import PickedGame
from picker_enums import PickerMode


def get_or_set(
    d: Dict[ExcelPlatform | str, int], plat: ExcelPlatform | str, _all: List[ExcelGame]
) -> int:
    val = d.get(plat)

    if val is not None:
        return val

    def filter_by_plat(_g: ExcelGame) -> bool:
        if _g.platform == ExcelPlatform.PC and _g.digital_platform is not None:
            return f"{_g.platform} ({_g.digital_platform})" == plat

        return _g.platform == plat

    d[plat] = len(list(filter(filter_by_plat, _all)))

    return d[plat]


def get_platform_progress_selector(data_provider: DataProvider) -> GameSelector:
    platform_progress: Dict[ExcelPlatform | str, int] = {}
    total_platform: Dict[ExcelPlatform | str, int] = {}

    def get_progress(
        kvp: Tuple[ExcelPlatform | str, List[PickedGame]]
    ) -> Tuple[float, float]:
        platform, _ = kvp
        played_games = data_provider.get_played_games()
        unplayed_candidates = data_provider.get_unplayed_candidates()

        return (
            get_or_set(
                platform_progress,
                platform,
                played_games,
            ),
            get_or_set(
                total_platform,
                platform,
                played_games + unplayed_candidates,
            ),
        )

    def get_progress_sort(
        kvp: Tuple[ExcelPlatform, List[PickedGame]]
    ) -> Tuple[float, int, str]:
        num, dem = get_progress(kvp)
        return (num / dem, -(dem - num), str.casefold(str(kvp[0])))

    return GameSelector(
        grouping=GameGrouping(
            sort=get_progress_sort,
            reverse=True,
            progress_indicator=get_progress,
        ),
        include_in_picks=False,
        include_platform=False,
        name="Platform Progress",
    )
