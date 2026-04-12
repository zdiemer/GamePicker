from typing import List, Optional

from excel_game import ExcelGame
from game_match import DataSource

from game_selector import GameSelector
from output_parser import OutputParser


def get_difficulty(game: ExcelGame, difficulties: List[int] = []) -> Optional[int]:
    gf_output = OutputParser.get_source_output(DataSource.GAME_FAQS)

    if game.hash_id in gf_output:
        difficulty = gf_output[game.hash_id].match_info.user_difficulty

        if difficulty is not None:
            if not any(difficulties) or round(difficulty) in difficulties:
                return difficulty

    return None


def get_difficulty_selector(difficulties: List[int], name: str) -> list[ExcelGame]:
    return GameSelector(
        lambda games: list(
            filter(
                lambda _g: _g.group_metadata is not None,
                (
                    g.get_copy_with_metadata(get_difficulty(g, difficulties))
                    for g in games
                ),
            )
        ),
        name=name,
        custom_suffix=lambda g: f" - {g.group_metadata}",
        sort=lambda pg: pg.game.group_metadata,
        reverse_sort=True,
    )
