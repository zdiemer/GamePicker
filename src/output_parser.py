from typing import Callable, Dict, List, Set, Tuple

# import csv
import jsonpickle
import os
import statistics

# from data_provider import DataProvider
from game_match import DataSource, GameMatch
from excel_game import ExcelGame, ExcelGenre
from output_constants import GENRE_MAPPINGS


class OutputParser:
    output_cache: Dict[DataSource, Dict[str, GameMatch]] = {}
    game_genres_cache: Dict[ExcelGame, Set[ExcelGenre]] = {}

    @staticmethod
    def get_source_output(source: DataSource) -> Dict[str, GameMatch]:
        if source in OutputParser.output_cache:
            return OutputParser.output_cache[source]

        output_root = "D:\\Code\\GameMaster\\output"
        source_folder = f"{output_root}\\{source.name.lower()}"

        game_match_dict: Dict[str, GameMatch] = {}

        for root, _, files in os.walk(source_folder):
            for file in files:
                if not file.startswith("matches-"):
                    continue

                with open(f"{root}/{file}", "r", encoding="utf-8") as f:
                    game_match_dict.update(jsonpickle.decode(f.read()))

        OutputParser.output_cache[source] = game_match_dict

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

    # @staticmethod
    # def create_output_csv() -> None:
    #     parser_outputs = {
    #         source: OutputParser.get_source_output(source)
    #         for source in list(DataSource)
    #     }

    #     csv_output = []
    #     data_provider = DataProvider()

    #     for game in data_provider.get_games():
    #         game_output = {
    #             "Title": game.title,
    #             "Platform": game.platform,
    #             "Release Date": (
    #                 game.release_date.strftime("%m/%d/%Y")
    #                 if game.release_date
    #                 else "Early Access"
    #             ),
    #             "Release Region": game.release_region.value,
    #             "Publisher": game.publisher,
    #             "Developer": game.developer,
    #             "Franchise": game.franchise,
    #             "Genre": game.genre.value,
    #         }

    #         for source in list(DataSource):
    #             game_match = parser_outputs[source].get(game.hash_id)
    #             source_name = source.name.replace("_", " ").title()
    #             if game_match is not None:
    #                 game_output[f"{source_name} Match Title"] = game_match.title
    #             else:
    #                 game_output[f"{source_name} Match Title"] = ""

    #         csv_output.append(game_output)

    #     with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
    #         fieldnames = [
    #             "Title",
    #             "Platform",
    #             "Release Date",
    #             "Release Region",
    #             "Publisher",
    #             "Developer",
    #             "Franchise",
    #             "Genre",
    #         ]

    #         fieldnames.extend(
    #             f"{source.name.replace('_', ' ').title()} Match Title"
    #             for source in list(DataSource)
    #         )

    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    #         writer.writeheader()
    #         writer.writerows(csv_output)

    @staticmethod
    def get_modified_critic_ratings(games: List[ExcelGame]) -> List[ExcelGame]:
        metacritic_output = OutputParser.get_source_output(DataSource.METACRITIC)
        output_games: List[ExcelGame] = []

        for game in games:
            g_copy = game.get_copy()

            if g_copy.hash_id in metacritic_output:
                score = (
                    metacritic_output[g_copy.hash_id]
                    .match_info.get("critics", {})
                    .get("score")
                )

                if score is not None:
                    g_copy.metacritic_rating = score / 100

            output_games.append(g_copy)

        return output_games

    @staticmethod
    def get_modified_user_ratings(games: List[ExcelGame]) -> List[ExcelGame]:
        gamefaqs_output = OutputParser.get_source_output(DataSource.GAME_FAQS)
        metacritic_output = OutputParser.get_source_output(DataSource.METACRITIC)
        moby_games_output = OutputParser.get_source_output(DataSource.MOBY_GAMES)
        vg_chartz_output = OutputParser.get_source_output(DataSource.VG_CHARTZ)
        vndb_output = OutputParser.get_source_output(DataSource.VNDB)
        output_games: List[ExcelGame] = []

        for game in games:
            ratings: List[float] = []
            g_copy = game.get_copy()

            if g_copy.gamefaqs_rating is not None:
                ratings.append(g_copy.gamefaqs_rating)

            if g_copy.hash_id in gamefaqs_output:
                score = gamefaqs_output[g_copy.hash_id].match_info.user_rating

                if score is not None:
                    ratings.append(score / 5)

            if g_copy.hash_id in metacritic_output:
                score = (
                    metacritic_output[g_copy.hash_id]
                    .match_info.get("users", {})
                    .get("score")
                )

                if score is not None:
                    ratings.append(score / 100)

            if g_copy.hash_id in moby_games_output:
                moby_score = moby_games_output[g_copy.hash_id].match_info.moby_score

                if moby_score is not None:
                    ratings.append(moby_score / 10)

            if g_copy.hash_id in vg_chartz_output:
                vg_chartz_score = vg_chartz_output[g_copy.hash_id].match_info.get(
                    "user_score"
                )

                if vg_chartz_score is not None:
                    ratings.append(vg_chartz_score / 10)

            if g_copy.hash_id in vndb_output:
                vndb_score = vndb_output[g_copy.hash_id].match_info.get("rating")

                if vndb_score is not None:
                    ratings.append(vndb_score / 100)

            g_copy.gamefaqs_rating = statistics.mean(ratings) if any(ratings) else None

            output_games.append(g_copy)

        return output_games

    @staticmethod
    def get_modified_hltb_time(games: List[ExcelGame]) -> List[ExcelGame]:
        hltb_output = OutputParser.get_source_output(DataSource.HLTB)
        output_games: List[ExcelGame] = []

        for game in games:
            g_copy = game.get_copy()

            if g_copy.hash_id in hltb_output:
                playtime_main = (
                    hltb_output[g_copy.hash_id].match_info.playtime_main_seconds // 60
                )

                if playtime_main > 60:
                    rem = playtime_main % 60
                    playtime_main -= rem
                    playtime_main += 30 * round(rem / 30)

                g_copy.estimated_playtime = playtime_main

            output_games.append(g_copy)

        return output_games

    @staticmethod
    def find_game(game: ExcelGame) -> List[GameMatch]:
        output_matches: List[Tuple[DataSource, GameMatch]] = []

        for source in list(DataSource):
            output = OutputParser.get_source_output(source)

            if game.hash_id in output:
                output_matches.append((source, output[game.hash_id]))

        return output_matches

    @staticmethod
    def get_game_genres(game: ExcelGame) -> Set[ExcelGenre]:
        if game in OutputParser.game_genres_cache:
            return OutputParser.game_genres_cache[game]

        game_matches = OutputParser.find_game(game)
        genres: Set[ExcelGenre] = set()

        for source, match in game_matches:
            if not GENRE_MAPPINGS.get(source):
                continue

            if source == DataSource.ARCADE_DATABASE:
                genres.add(GENRE_MAPPINGS[source][match.match_info.genre])
            if source == DataSource.COOPTIMUS:
                genres.add(GENRE_MAPPINGS[source][match.match_info["genre"]])
            if source == DataSource.GAME_FAQS:
                genre_or_genres = GENRE_MAPPINGS[source][
                    match.match_info.genre.full_name
                ]

                if isinstance(genre_or_genres, list):
                    genres.update(set(genre_or_genres))
                else:
                    genres.add(genre_or_genres)
            if source == DataSource.GAME_SPOT:
                genre = " ".join(
                    sorted(_g["name"] for _g in match.match_info.get("genres", []))
                )

                genre_or_genres = GENRE_MAPPINGS[source].get(genre)

                if isinstance(genre_or_genres, list):
                    genres.update(set(genre_or_genres))
                else:
                    genres.add(genre_or_genres)
            if source == DataSource.IGN:
                for genre in match.match_info["genres"]:
                    genre_or_genres = GENRE_MAPPINGS[source].get(genre["name"])

                    if isinstance(genre_or_genres, list):
                        genres.update(set(genre_or_genres))
                    else:
                        genres.add(genre_or_genres)

        OutputParser.game_genres_cache[game] = set(
            filter(lambda g: g is not None, genres)
        )

        return OutputParser.game_genres_cache[game]
