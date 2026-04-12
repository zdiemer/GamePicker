from excel_game import ExcelGame
from game_match import DataSource

from data_provider import DataProvider
from game_selector import GameSelector
from output_parser import OutputParser
from picker_enums import PickerMode


def get_no_output_matches_selector(data_provider: DataProvider) -> GameSelector:
    outputs = {
        source: OutputParser.get_source_output(source) for source in list(DataSource)
    }

    def is_in_any_output(game: ExcelGame) -> bool:
        return any(game.hash_id in output for output in outputs.values())

    return GameSelector(
        _filter=lambda game: not is_in_any_output(game),
        games=data_provider.get_games(),
        name="No Output Matches",
        include_in_picks=False,
        run_on_modes=set([PickerMode.ALL]),
    )
