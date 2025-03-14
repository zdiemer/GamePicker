from typing import List

from excel_game import ExcelGame
from game_match import DataSource
from game_grouping import GameGrouping
from game_selector import GameSelector
from output_parser import OutputParser


def coop_games(games: List[ExcelGame]) -> List[ExcelGame]:
    coop = OutputParser.get_source_output(DataSource.COOPTIMUS)
    output: List[ExcelGame] = []

    for game in games:
        if game.hash_id in coop:
            game.group_metadata = coop[game.hash_id].match_info
            output.append(game)

    return output


COOP_GAMES = GameSelector(
    coop_games,
    grouping=GameGrouping(
        lambda g: (
            "Local"
            if g.group_metadata["local"]
            else "Online" if g.group_metadata["online"] else "LAN"
        ),
    ),
    custom_suffix=lambda g: f" ({', '.join(sorted(g.group_metadata['features']))})",
    include_platform=True,
    sort=lambda pg: pg.game.combined_rating,
    reverse_sort=True,
)
