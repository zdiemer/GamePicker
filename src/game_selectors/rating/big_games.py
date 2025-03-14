from game_match import DataSource
from game_selector import GameSelector
from output_parser import OutputParser
from picker_enums import PickerMode

BIG_GAMES = GameSelector(
    lambda games: OutputParser.get_source_output_filtered(
        games,
        DataSource.METACRITIC,
        lambda g: ((g.match_info.get("users") or {}).get("reviewCount") or 0) > 25,
    ),
    name="Big Games",
    run_on_modes=set([PickerMode.ALL]),
)
