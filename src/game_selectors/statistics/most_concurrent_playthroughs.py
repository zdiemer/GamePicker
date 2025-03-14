from typing import Dict, List, Set
import datetime

from excel_game import ExcelGame
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


class PlaythroughPoint:
    date: datetime.datetime
    game: ExcelGame
    end: bool

    def __init__(self, game: ExcelGame, date: datetime.datetime, end: bool):
        self.game = game
        self.date = date
        self.end = end


def get_playthrough_days(
    games: List[ExcelGame],
) -> List[ExcelGame]:
    dates: List[PlaythroughPoint] = []
    concurrent: Set[ExcelGame] = set()
    concurrent_games: Dict[datetime.datetime, Set[ExcelGame]] = {}

    for game in games:
        if game.date_started is not None:
            dates.append(PlaythroughPoint(game, game.date_started, False))
        if game.date_completed is not None:
            dates.append(PlaythroughPoint(game, game.date_completed, True))

    dates.sort(key=lambda x: (x.date, x.end))

    for point in dates:
        point_games: Set[ExcelGame] = set()

        if point.end:
            if point.game in concurrent:
                concurrent.remove(point.game)
            else:
                point_games.add(point.game)
        else:
            if (
                point.game.date_completed is not None
                or point.game.playing_status is not None
            ):
                concurrent.add(point.game)
            else:
                point_games.add(point.game)

        date_games = set(
            g.get_copy_with_metadata(point.date) for g in concurrent.union(point_games)
        )

        if point.date in concurrent_games:
            concurrent_games[point.date].update(date_games)
        else:
            concurrent_games[point.date] = date_games

    return [game for games in concurrent_games.values() for game in games]


def get_most_concurrent_playthroughs_selector(
    data_provider: DataProvider,
) -> GameSelector:
    return GameSelector(
        get_playthrough_days,
        _filter=lambda g: g.date_started is not None or g.date_completed is not None,
        name="Most Concurrent Playthroughs",
        games=data_provider.get_games(),
        grouping=GameGrouping(
            lambda g: g.group_metadata,
            get_group_name=lambda kvp: f"{kvp[0].strftime('%B %d, %Y')} ({len(kvp[1]):,})",
            should_rank=False,
            sort=lambda kvp: len(kvp[1]),
            reverse=True,
        ),
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
        custom_suffix=lambda g: (
            (
                f" [{g.date_started.strftime('%m/%d/%Y')}]"
                if g.date_started is not None
                else ""
            )
            + (
                " -"
                if g.date_started is not None
                and (g.date_completed is not None or g.playing_status is not None)
                else ""
            )
            + (
                f" [{g.date_completed.strftime('%m/%d/%Y')}]"
                if g.date_completed is not None
                else (" Ongoing" if g.playing_status is not None else "")
            )
        ),
        group_count=50,
    )
