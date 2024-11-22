from typing import Callable, Dict, List

import jsonpickle
import os

from game_match import DataSource, GameMatch
from excel_game import ExcelGame


class OutputParser:
    @staticmethod
    def get_source_output(source: DataSource) -> Dict[str, GameMatch]:
        output_root = "D:\\Code\\GameMaster\\output"
        source_folder = f"{output_root}\\{source.name.lower()}"

        game_match_dict: Dict[str, GameMatch] = {}

        for root, _, files in os.walk(source_folder):
            for file in files:
                if not file.startswith("matches-"):
                    continue

                with open(f"{root}/{file}", "r", encoding="utf-8") as f:
                    game_match_dict.update(jsonpickle.decode(f.read()))

        return game_match_dict

    @staticmethod
    def get_source_output_filtered(
        games: List[ExcelGame],
        source: DataSource,
        match_condition: Callable[[GameMatch], bool],
    ) -> List[ExcelGame]:
        parser_output = OutputParser.get_source_output(source)
        parser_output = {k: v for k, v in parser_output.items() if match_condition(v)}

        filtered = list(filter(lambda g: g.hash_id in parser_output, games))

        for g in filtered:
            g.group_metadata = parser_output[g.hash_id].match_info

        return filtered
