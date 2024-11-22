from typing import List

from excel_game import ExcelGenre
from game_selector import GameSelector


def get_genre_selector(genre: ExcelGenre, name: str) -> GameSelector:
    return GameSelector(_filter=lambda game: game.genre == genre, name=name)


def get_multi_genre_selector(genres: List[ExcelGenre], name: str) -> GameSelector:
    return GameSelector(_filter=lambda game: game.genre in genres, name=name)
