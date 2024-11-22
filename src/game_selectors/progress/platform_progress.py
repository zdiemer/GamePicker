from typing import Dict, List, Tuple

from excel_game import ExcelGame, ExcelPlatform
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picked_game import PickedGame


def get_or_set(
    d: Dict[ExcelPlatform, int], plat: ExcelPlatform, _all: List[ExcelGame]
) -> int:
    val = d.get(plat)

    if val is not None:
        return val

    d[plat] = len(list(filter(lambda g: g.platform == plat, _all)))

    return d[plat]


def get_platform_progress_selector(data_provider: DataProvider) -> GameSelector:
    played_games = data_provider.get_played_games()
    unplayed_candidates = data_provider.get_unplayed_candidates()

    platform_progress: Dict[ExcelPlatform, int] = {}
    total_platform: Dict[ExcelPlatform, int] = {}

    def get_progress(
        kvp: Tuple[ExcelPlatform, List[PickedGame]]
    ) -> Tuple[float, float]:
        platform, _ = kvp
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

    def get_progress_float(kvp: Tuple[ExcelPlatform, List[PickedGame]]) -> float:
        num, dem = get_progress(kvp)
        return num / dem

    return GameSelector(
        grouping=GameGrouping(
            sort=get_progress_float,
            reverse=True,
            progress_indicator=get_progress,
        ),
        include_in_picks=False,
        name="Platform Progress",
    )
