from typing import List

from excel_game import ExcelGame
from excel_parser import ExcelParser
from game_match import DataSource
from match_validator import MatchValidator
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from output_parser import OutputParser
from picker_enums import PickerMode


def get_non_matched_games(games: List[ExcelGame]) -> List[ExcelGame]:
    outputs = {
        source: OutputParser.get_source_output(source) for source in list(DataSource)
    }

    def is_in_output(game: ExcelGame, source: DataSource) -> bool:
        return game.hash_id in outputs[source]

    parser = ExcelParser()

    output_games: List[ExcelGame] = []

    for game in games:
        output_games.append(
            game.get_copy_with_metadata(
                {source: is_in_output(game, source) for source in list(DataSource)}
            )
        )

    clients = {
        source: parser._ALL_CLIENTS[source](MatchValidator())
        for source in list(DataSource)
    }

    output_matched = {
        source: [
            (
                game,
                game.group_metadata[source] is True,
            )
            for game in output_games
            if not clients[source].should_skip(game)
        ]
        for source in DataSource
    }

    not_matched: List[ExcelGame] = []

    for source, _games in output_matched.items():
        for game, matched in _games:
            if matched is False:
                not_matched.append(game.get_copy_with_metadata(source))

    return not_matched


def get_output_match_rate_selector(data_provider: DataProvider) -> GameSelector:
    outputs = {
        source: OutputParser.get_source_output(source) for source in list(DataSource)
    }

    def is_in_output(game: ExcelGame, source: DataSource) -> bool:
        return game.hash_id in outputs[source]

    parser = ExcelParser()

    output_games: List[ExcelGame] = []

    for game in data_provider.get_games():
        output_games.append(
            game.get_copy_with_metadata(
                {source: is_in_output(game, source) for source in list(DataSource)}
            )
        )

    clients = {
        source: parser._ALL_CLIENTS[source](MatchValidator())
        for source in list(DataSource)
    }

    output_matched = {
        source: [
            (
                game,
                game.group_metadata[source] is True,
            )
            for game in output_games
            if not clients[source].should_skip(game)
        ]
        for source in DataSource
    }

    output_match_rates = {
        source: (
            sum(1 for _, matched in output_matched[source] if matched is True),
            (
                sum(1 for _, matched in output_matched[source] if matched is True)
                / len(output_matched[source])
                if len(output_matched[source]) > 0
                else 0
            ),
        )
        for source in DataSource
    }

    not_matched: List[ExcelGame] = []

    for source, games in output_matched.items():
        for game, matched in games:
            if matched is False:
                not_matched.append(game.get_copy_with_metadata(source))

    return GameSelector(
        games=not_matched,
        name="Output Match Rate",
        include_in_picks=False,
        run_on_modes=set([PickerMode.ALL]),
        grouping=GameGrouping(
            lambda g: f"{g.group_metadata.value} ({output_match_rates[g.group_metadata][0]:,}/{len(output_matched[g.group_metadata]):,}, {output_match_rates[g.group_metadata][1]:.0%})",
            should_rank=False,
            group_size=0,
        ),
    )
