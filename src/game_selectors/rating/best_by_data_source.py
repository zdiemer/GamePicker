from typing import List
import math

from excel_game import ExcelGame
from game_match import DataSource
from game_grouping import GameGrouping
from game_selector import GameSelector
from output_parser import OutputParser


def get_games_with_metadata(games: List[ExcelGame]) -> List[ExcelGame]:
    output: List[ExcelGame] = []

    game_faqs_output = OutputParser.get_source_output(DataSource.GAME_FAQS)
    launchbox_output = OutputParser.get_source_output(DataSource.LAUNCHBOX)
    metacritic_output = OutputParser.get_source_output(DataSource.METACRITIC)
    moby_games_output = OutputParser.get_source_output(DataSource.MOBY_GAMES)
    steam_output = OutputParser.get_source_output(DataSource.STEAM)
    vg_chartz_output = OutputParser.get_source_output(DataSource.VG_CHARTZ)
    vndb_output = OutputParser.get_source_output(DataSource.VNDB)

    for game in games:
        if (
            (source_output := game_faqs_output.get(game.hash_id)) is not None
            and source_output.match_info.user_rating is not None
            and source_output.match_info.user_rating > 0
        ):
            output.append(
                game.get_copy_with_metadata(
                    (
                        DataSource.GAME_FAQS,
                        source_output.match_info.user_rating / 5,
                        source_output.match_info.user_rating_count,
                    )
                )
            )

        if (
            (source_output := launchbox_output.get(game.hash_id)) is not None
            and source_output.match_info.get("communityRating") is not None
            and source_output.match_info.get("communityRating") > 0
        ):
            output.append(
                game.get_copy_with_metadata(
                    (
                        DataSource.LAUNCHBOX,
                        source_output.match_info.get("communityRating") / 5,
                        source_output.match_info.get("totalVotes"),
                    )
                )
            )

        if (
            (source_output := metacritic_output.get(game.hash_id)) is not None
            and source_output.match_info.get("user", {}).get("score") is not None
            and source_output.match_info.get("user", {}).get("score") > 0
        ):
            output.append(
                game.get_copy_with_metadata(
                    (
                        DataSource.METACRITIC,
                        source_output.match_info.get("user").get("score") / 100,
                        source_output.match_info.get("user").get("reviewCount"),
                    )
                )
            )

        if (
            (source_output := moby_games_output.get(game.hash_id)) is not None
            and source_output.match_info.moby_score is not None
            and source_output.match_info.moby_score > 0
        ):
            output.append(
                game.get_copy_with_metadata(
                    (
                        DataSource.MOBY_GAMES,
                        source_output.match_info.moby_score / 10,
                        source_output.match_info.num_votes,
                    )
                )
            )

        if (source_output := steam_output.get(game.hash_id)) is not None:
            query_summary = source_output.match_info["app_reviews"].get("query_summary")

            if (
                query_summary is not None
                and "total_positive" in query_summary
                and "total_reviews" in query_summary
                and query_summary["total_reviews"] > 0
            ):
                output.append(
                    game.get_copy_with_metadata(
                        (
                            DataSource.STEAM,
                            query_summary["total_positive"]
                            / query_summary["total_reviews"],
                            query_summary["total_reviews"],
                        )
                    )
                )

        if (
            (source_output := vg_chartz_output.get(game.hash_id)) is not None
            and source_output.match_info.get("user_score") is not None
            and source_output.match_info.get("user_score") > 0
        ):
            output.append(
                game.get_copy_with_metadata(
                    (
                        DataSource.VG_CHARTZ,
                        source_output.match_info.get("user_score") / 10,
                        None,
                    )
                )
            )

        if (
            (source_output := vndb_output.get(game.hash_id)) is not None
            and source_output.match_info.get("rating") is not None
            and source_output.match_info.get("rating") > 0
        ):
            output.append(
                game.get_copy_with_metadata(
                    (
                        DataSource.VNDB,
                        source_output.match_info.get("rating") / 100,
                        source_output.match_info.get("votecount"),
                    )
                )
            )

    return output


def agresti_coull_lower(n: int, k: int) -> float:
    kappa = 2.24140273  # 95% confidence interval
    kest = k + kappa**2 / 2
    nest = n + kappa**2
    pest = kest / nest
    radius = kappa * math.sqrt(pest * (1 - pest) / nest)
    return max(0, pest - radius)


BEST_BY_DATA_SOURCE_SELECTOR = GameSelector(
    get_games_with_metadata,
    name="Best By Data Source",
    custom_suffix=lambda g: f" - {g.group_metadata[1]:.0%} {'(' + str(g.group_metadata[2]) + ' rating' + ('s' if g.group_metadata[2] != 1 else '') + ')' if g.group_metadata[2] is not None else ''}",
    sort=lambda pg: (
        pg.game.group_metadata[1]
        if pg.game.group_metadata[2] is None
        else agresti_coull_lower(
            pg.game.group_metadata[2],
            pg.game.group_metadata[1] * pg.game.group_metadata[2],
        )
    ),
    grouping=GameGrouping(lambda g: g.group_metadata[0].value, group_size=100),
    reverse_sort=True,
)
