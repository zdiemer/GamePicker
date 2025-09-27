from typing import List

from excel_game import ExcelGenre
from game_selector import GameSelector
from output_parser import OutputParser

ENABLE_OUTPUT_PARSER = False


def get_genre_selector(genre: ExcelGenre, name: str) -> GameSelector:
    return GameSelector(
        _filter=lambda game: game.genre == genre
        or (ENABLE_OUTPUT_PARSER and genre in OutputParser.get_game_genres(game)),
        name=name,
    )


def get_multi_genre_selector(genres: List[ExcelGenre], name: str) -> GameSelector:
    return GameSelector(
        _filter=lambda game: game.genre in genres
        or (
            ENABLE_OUTPUT_PARSER
            and any(genre in OutputParser.get_game_genres(game) for genre in genres)
        ),
        name=name,
    )
