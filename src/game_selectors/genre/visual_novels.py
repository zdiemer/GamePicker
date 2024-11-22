from typing import List

from excel_game import ExcelGame, ExcelGenre
from game_match import DataSource
from game_selector import GameSelector
from output_parser import OutputParser


def visual_novels(games: List[ExcelGame]) -> List[ExcelGame]:
    vndb_games = OutputParser.get_source_output(DataSource.VNDB)
    output: List[ExcelGame] = []

    for game in games:
        if game.genre == ExcelGenre.VISUAL_NOVEL or game.hash_id in vndb_games:
            output.append(game)

    return output


VISUAL_NOVELS = GameSelector(visual_novels)
