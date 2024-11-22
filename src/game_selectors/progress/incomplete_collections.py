from typing import List
from excel_game import ExcelGame
from data_provider import DataProvider
from game_selector import GameSelector
from picker_enums import PickerMode


def incomplete_collections(data_provider: DataProvider) -> List[ExcelGame]:
    games, _ = data_provider.get_excel_loader().merge()

    incomplete: List[ExcelGame] = []

    for g in games:
        if any(g.child_games) and not g.completed:
            incomplete.append(g)

    return incomplete


def get_incomplete_collections_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        lambda _: incomplete_collections(data_provider),
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
        name="Incomplete Collections",
    )
