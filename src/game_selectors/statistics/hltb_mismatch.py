from typing import List

from excel_game import ExcelGame
from game_match import DataSource

from data_provider import DataProvider
from game_selector import GameSelector
from output_parser import OutputParser
from picker_enums import PickerMode


def get_hltb_mismatch_selector(data_provider: DataProvider) -> GameSelector:
    hltb_output = OutputParser.get_source_output(DataSource.HLTB)

    games = list(filter(lambda g: not g.completed, data_provider.get_games()))
    c_games: List[ExcelGame] = []

    for game in games:
        g_copy = game.get_copy()

        if g_copy.hash_id in hltb_output:
            playtime_min = (
                hltb_output[g_copy.hash_id].match_info.playtime_main_seconds // 60
            )

            if playtime_min > 60:
                rem = playtime_min % 60
                playtime_min -= rem
                playtime_min += 30 * round(rem / 30)

            g_copy.group_metadata = playtime_min / 60

        c_games.append(g_copy)

    return GameSelector(
        _filter=lambda game: game.group_metadata is not None
        and game.estimated_playtime is None,
        games=c_games,
        name="HLTB Missing Playtime",
        include_in_picks=False,
        run_on_modes=set([PickerMode.ALL]),
        custom_suffix=lambda g: (
            f" - {g.group_metadata:.0f}hr"
            if g.group_metadata >= 1
            else f" - {int(g.group_metadata * 60)}min"
        ),
    )
