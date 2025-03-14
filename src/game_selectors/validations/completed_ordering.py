import copy
import datetime
from typing import List, Optional, Tuple
from excel_game import ExcelGame

from data_provider import DataProvider
from game_selector import GameSelector
from game_grouping import GameGrouping
from picker_enums import PickerMode


def find_closest_completed_date_after_date(
    games: List[ExcelGame], date: datetime.datetime
) -> Tuple[Optional[int], Optional[ExcelGame]]:
    closest_delta: Optional[datetime.timedelta] = None
    closest_game: Optional[ExcelGame] = None
    closest_idx: Optional[int] = None

    for idx, g in enumerate(games):
        if g.date_completed is not None and g.date_completed > date:
            if closest_delta is None or g.date_completed - date < closest_delta:
                closest_delta = g.date_completed - date
                closest_game = g
                closest_idx = idx

    return (closest_idx, closest_game)


def completed_ordering(games: List[ExcelGame]) -> List[ExcelGame]:
    by_completed_num: List[ExcelGame] = sorted(
        games,
        key=lambda g: g.completion_number,
    )

    completed_ordered: List[ExcelGame] = []
    latest_date: Optional[datetime.datetime] = None

    for g in by_completed_num:
        if g.date_completed is not None and (
            latest_date is None or g.date_completed >= latest_date
        ):
            latest_date = g.date_completed
            completed_ordered.append(copy.copy(g))
        elif g.date_completed is None:
            completed_ordered.append(copy.copy(g))
        else:
            closest_idx, _ = find_closest_completed_date_after_date(
                completed_ordered, g.date_completed
            )

            if closest_idx is not None:
                completed_ordered.insert(
                    closest_idx, g.get_copy_with_metadata(g.completion_number)
                )

    for idx, g in enumerate(completed_ordered):
        g.completion_number = idx + 1

    return completed_ordered


def get_suffix(game: ExcelGame) -> str:
    suffix = ""
    if game.date_completed:
        suffix += f" ({game.date_completed.strftime('%B %d, %Y')})"
    if game.group_metadata:
        suffix += f" [Original Completion: {game.group_metadata}]"
    return suffix


def get_completed_ordering_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        completed_ordering,
        games=data_provider.get_completed_games(),
        grouping=GameGrouping(lambda _: "Ordered", should_rank=False),
        name="Completed Ordering",
        sort=lambda g: g.game.completion_number,
        custom_prefix=lambda g: f"{g.completion_number}. ",
        custom_suffix=get_suffix,
        run_on_modes=set([PickerMode.ALL]),
    )
