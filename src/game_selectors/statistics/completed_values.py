from typing import List
from excel_game import ExcelGame, ExcelOwnedCondition, ExcelOwnedFormat
from game_match import DataSource
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from output_parser import OutputParser
from picker_enums import PickerMode

CONDIITON_MAPPING = {
    ExcelOwnedCondition.COMPLETE: "CIB",
    ExcelOwnedCondition.GAME_ONLY: "Loose",
    ExcelOwnedCondition.GAME_AND_BOX_ONLY: "Loose",
}


def completed_values(games: List[ExcelGame]) -> List[ExcelGame]:
    gameeye_output = OutputParser.get_source_output(DataSource.GAMEYE)
    priced_games: List[ExcelGame] = []

    filtered = list(filter(lambda g: g.hash_id in gameeye_output, games))

    for game in filtered:
        owned_type = CONDIITON_MAPPING[game.owned_condition]
        if (
            gameeye_output[game.hash_id].match_info.get("price") is None
            or owned_type not in gameeye_output[game.hash_id].match_info["price"]
        ):
            continue

        game.group_metadata = float(
            gameeye_output[game.hash_id].match_info["price"][owned_type]
        )
        priced_games.append(game)

    return priced_games


def get_completed_values_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        completed_values,
        run_on_modes=set([PickerMode.ALL]),
        games=list(
            filter(
                lambda g: g.owned_format
                in (ExcelOwnedFormat.BOTH, ExcelOwnedFormat.PHYSICAL),
                data_provider.get_played_games(),
            )
        ),
        include_in_picks=False,
        grouping=GameGrouping(
            lambda g: (
                CONDIITON_MAPPING[g.owned_condition]
                if isinstance(g.group_metadata, float)
                else "Missing"
            ),
            should_rank=False,
            get_group_name=lambda kvp: (
                f"{kvp[0]} (${sum(g.game.group_metadata for g in kvp[1]) / 100:,.2f})"
                if kvp[0] != "Missing"
                else kvp[0]
            ),
        ),
        custom_suffix=lambda g: (
            f" - ${g.group_metadata / 100:,.2f}" if g.group_metadata is not None else ""
        ),
        sort=lambda g: g.game.group_metadata,
        reverse_sort=True,
    )
