from excel_game import ExcelGame
from game_match import DataSource
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from output_parser import OutputParser
from picker_enums import PickerMode


def get_custom_suffix(g: ExcelGame, hltb_hours: float) -> str:
    playtime_difference = g.completion_time - hltb_hours

    return (
        f"\n        - Difference: {playtime_difference:+0.1f}"
        f"\n        - HLTB: {hltb_hours:0.1f}"
        f"\n        - Personal: {g.completion_time:0.1f}\n"
    )


def get_largest_playtime_differences_selector(
    data_provider: DataProvider,
) -> GameSelector:
    hltb_output = OutputParser.get_source_output(DataSource.HLTB)

    return GameSelector(
        lambda _: list(
            filter(
                lambda g: (g.completion_time is not None and g.hash_id in hltb_output),
                data_provider.get_played_games(),
            )
        ),
        name="Largest Playtime Differences",
        sort=lambda g: abs(
            g.game.completion_time
            - hltb_output[g.game.hash_id].match_info.playtime_main_seconds / 3600
        ),
        reverse_sort=True,
        custom_suffix=lambda g: get_custom_suffix(
            g, hltb_output[g.hash_id].match_info.playtime_main_seconds / 3600
        ),
        grouping=GameGrouping(
            lambda _: "Largest Playtime Differences",
            group_size=100,
            should_rank=False,
        ),
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
    )
