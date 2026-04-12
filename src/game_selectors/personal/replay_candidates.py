import datetime

from data_provider import DataProvider
from game_selector import GameSelector


def get_replay_candidates_selector(
    data_provider: DataProvider,
):
    now = datetime.datetime.now()

    return GameSelector(
        _filter=lambda g: g.rating >= 0.8
        and (
            g.date_completed is None
            or g.date_completed < now - datetime.timedelta(days=365 * 5)
        ),
        name="Replay Candidates",
        games=data_provider.get_played_games(),
    )
