from enum import Enum
from typing import Dict, List, Set

import asyncio
import numpy as np

from clients import (
    BackloggdClient,
    DatePart,
    GiantBombClient,
    MobyGamesClient,
    RateLimit,
)
from excel_game import ExcelGame
from excel_loader import ExcelLoader
from game_match import DataSource
from match_validator import MatchValidator

from excel_backed_cache import ExcelBackedCache
from excel_filter import ExcelFilter
from output_parser import OutputParser


class Percentile(Enum):
    P1 = 0
    P5 = 1
    P10 = 2
    P25 = 3
    MED = 4
    P75 = 5
    P90 = 6
    P95 = 7
    P99 = 8


class DataProvider:
    _games: List[ExcelGame]
    _completed_games: List[ExcelGame]
    _games_on_order: List[ExcelGame]
    _unplayed_candidates: List[ExcelGame]
    _validator: MatchValidator
    _bcclient: BackloggdClient
    _gbclient: GiantBombClient
    _mbclient: MobyGamesClient
    _cache: ExcelBackedCache
    _mbcache: Dict[int, Set[str]]
    _gbcache: Dict[str, Set[str]]
    _loader: ExcelLoader
    _name_collisions: Dict[str, int]

    _percentiles: Dict[Percentile, float]

    __BASE_DROPBOX_FOLDER = "C:\\Users\\zachd\\Dropbox\\Video Game Lists"
    __EXCEL_SHEET_NAME = "Games Master List - Final.xlsx"
    __CACHE_FILE_NAME = "cache.pkl"
    __MOBY_GAMES_CACHE_FILE_NAME = "mbcache.pkl"
    __GIANT_BOMB_CACHE_FILE_NAME = "gbcache.pkl"

    def __init__(self, no_cache: bool = False, load_sources: bool = True):
        self._cache = ExcelBackedCache()
        self._validator = MatchValidator()
        self._bcclient = BackloggdClient(self._validator)
        self._gbclient = GiantBombClient(self._validator)
        self._mbclient = MobyGamesClient(
            self._validator, rate_limit=RateLimit(1, DatePart.SECOND)
        )
        self._name_collisions = {}

        self._loader = ExcelLoader(self.__get_excel_file_name())

        if not no_cache:
            cache_data = self._cache.load(self.__CACHE_FILE_NAME)
            self._mbcache = (
                self._cache.load(
                    self.__MOBY_GAMES_CACHE_FILE_NAME, use_excel_modify_date=False
                )
                or {}
            )

            self._gbcache = (
                self._cache.load(
                    self.__GIANT_BOMB_CACHE_FILE_NAME, use_excel_modify_date=False
                )
                or {}
            )

            if cache_data is not None:
                (
                    self._games,
                    self._played_games,
                    self._unplayed_candidates,
                    self._completed_games,
                    self._games_on_order,
                ) = cache_data

                p1, p5, p10, p25, med, p75, p90, p95, p99 = np.percentile(
                    [g.combined_rating for g in self._games],
                    [1, 5, 10, 25, 50, 75, 90, 95, 99],
                )

                self._percentiles = {
                    Percentile.P1: p1,
                    Percentile.P5: p5,
                    Percentile.P10: p10,
                    Percentile.P25: p25,
                    Percentile.MED: med,
                    Percentile.P75: p75,
                    Percentile.P90: p90,
                    Percentile.P95: p95,
                    Percentile.P99: p99,
                }

                for g in self._games:
                    if g.game_platform_hash_id in self._name_collisions:
                        self._name_collisions[g.game_platform_hash_id] += 1
                    else:
                        self._name_collisions[g.game_platform_hash_id] = 1
                return
        else:
            self._mbcache = {}
            self._gbcache = {}

        self._games = self._loader.games

        p1, p5, p10, p25, med, p75, p90, p95, p99 = np.percentile(
            [g.combined_rating for g in self._games], [1, 5, 10, 25, 50, 75, 90, 95, 99]
        )

        self._percentiles = {
            Percentile.P1: p1,
            Percentile.P5: p5,
            Percentile.P10: p10,
            Percentile.P25: p25,
            Percentile.MED: med,
            Percentile.P75: p75,
            Percentile.P90: p90,
            Percentile.P95: p95,
            Percentile.P99: p99,
        }

        if load_sources:
            print("Loading Data Sources")
            gamefaqs_output = OutputParser.get_source_output(DataSource.GAME_FAQS)
            hltb_output = OutputParser.get_source_output(DataSource.HLTB)
            metacritic_output = OutputParser.get_source_output(DataSource.METACRITIC)
            mobygames_output = OutputParser.get_source_output(DataSource.MOBY_GAMES)
            vg_chartz_output = OutputParser.get_source_output(DataSource.VG_CHARTZ)
            vndb_output = OutputParser.get_source_output(DataSource.VNDB)
            steam_output = OutputParser.get_source_output(DataSource.STEAM)

            for g in self._games:
                if g.game_platform_hash_id in self._name_collisions:
                    self._name_collisions[g.game_platform_hash_id] += 1
                else:
                    self._name_collisions[g.game_platform_hash_id] = 1

                if g.gamefaqs_rating is None:
                    if g.hash_id in gamefaqs_output:
                        g_score = gamefaqs_output[g.hash_id].match_info.user_rating

                        if g_score is not None and g_score > 0:
                            g.gamefaqs_rating = g_score / 5
                    elif g.hash_id in steam_output:
                        query_summary = (
                            steam_output[g.hash_id]
                            .match_info["app_reviews"]
                            .get("query_summary")
                        )

                        if (
                            query_summary is not None
                            and "total_positive" in query_summary
                            and "total_reviews" in query_summary
                            and query_summary["total_reviews"] > 0
                        ):
                            g.gamefaqs_rating = (
                                query_summary["total_positive"]
                                / query_summary["total_reviews"]
                            )
                    elif g.hash_id in metacritic_output:
                        mu_score = (
                            metacritic_output[g.hash_id]
                            .match_info.get("users", {})
                            .get("score")
                        )

                        if mu_score is not None and mu_score > 0:
                            g.gamefaqs_rating = mu_score / 100
                    elif g.hash_id in mobygames_output:
                        mo_score = mobygames_output[g.hash_id].match_info.moby_score

                        if mo_score is not None and mo_score > 0:
                            g.gamefaqs_rating = mo_score / 10
                    elif g.hash_id in vg_chartz_output:
                        vg_score = vg_chartz_output[g.hash_id].match_info.get(
                            "user_score"
                        )

                        if vg_score is not None and vg_score > 0:
                            g.gamefaqs_rating = vg_score / 10
                    elif g.hash_id in vndb_output:
                        vn_score = vndb_output[g.hash_id].match_info.get("rating")

                        if vn_score is not None and vn_score > 0:
                            g.gamefaqs_rating = vn_score / 100

                if g.metacritic_rating is None:
                    if g.hash_id in metacritic_output:
                        m_score = (
                            metacritic_output[g.hash_id]
                            .match_info.get("users", {})
                            .get("score")
                        )

                        if m_score is not None and m_score > 0:
                            g.metacritic_rating = m_score / 100
                    elif g.hash_id in steam_output:
                        sc_score = (
                            steam_output[g.hash_id]
                            .match_info["app_details"]
                            .get("data", {})
                            .get("metacritic", {})
                            .get("score")
                        )

                        if sc_score is not None and sc_score > 0:
                            g.metacritic_rating = sc_score / 100

                if not g.completed and g.estimated_playtime is None:
                    if g.hash_id in hltb_output:
                        playtime_min = (
                            hltb_output[g.hash_id].match_info.playtime_main_seconds
                            // 60
                        )

                        if playtime_min > 60:
                            rem = playtime_min % 60
                            playtime_min -= rem
                            playtime_min += 30 * round(rem / 30)

                        if playtime_min is not None and playtime_min > 0:
                            g.estimated_playtime = playtime_min / 60
                    elif g.hash_id in gamefaqs_output:
                        playtime_hours = gamefaqs_output[
                            g.hash_id
                        ].match_info.user_length_hours

                        if playtime_hours is not None and playtime_hours > 0:
                            playtime_hours = playtime_hours - (playtime_hours % 0.5)
                            g.estimated_playtime = playtime_hours
                    elif g.hash_id in vndb_output:
                        playtime_min = vndb_output[g.hash_id].match_info.get(
                            "length_minutes"
                        )

                        if playtime_min is not None and playtime_min > 0:
                            playtime_min = playtime_min // 60

                            if playtime_min > 60:
                                rem = playtime_min % 60
                                playtime_min -= rem
                                playtime_min += 30 * round(rem / 30)

                            if playtime_min > 0:
                                g.estimated_playtime = playtime_min / 60

        self._played_games = list(
            filter(
                lambda game: game.completed,
                self._games,
            )
        )

        self._unplayed_candidates = list(
            filter(
                lambda g: ExcelFilter.is_not_low_priority(g)
                and ExcelFilter.is_playable(g)
                and ExcelFilter.is_playable_by_language(g)
                and ExcelFilter.is_unplayed(g)
                and ExcelFilter.is_released(g),
                self._games,
            )
        )

        self._completed_games = self._loader.completed_games
        self._games_on_order = self._loader.games_on_order

        self._cache.write(
            self.__CACHE_FILE_NAME,
            (
                self._games,
                self._played_games,
                self._unplayed_candidates,
                self._completed_games,
                self._games_on_order,
            ),
        )

    def __get_excel_file_name(self) -> str:
        return f"{self.__BASE_DROPBOX_FOLDER}\\{self.__EXCEL_SHEET_NAME}"

    def get_name_collisions(self) -> Dict[str, int]:
        return self._name_collisions

    def get_excel_loader(self) -> ExcelLoader:
        return self._loader

    def get_giant_bomb_cache(self) -> Dict[str, Set[str]]:
        return self._gbcache

    def get_moby_games_cache(self) -> Dict[str, Set[str]]:
        return self._mbcache

    def get_games(self) -> List[ExcelGame]:
        return self._games

    def get_completed_games(self) -> List[ExcelGame]:
        return self._completed_games

    def get_games_on_order(self) -> List[ExcelGame]:
        return self._games_on_order

    def get_unplayed_candidates(self) -> List[ExcelGame]:
        return self._unplayed_candidates

    def get_played_games(self) -> List[ExcelGame]:
        return self._played_games

    def get_cache(self) -> ExcelBackedCache:
        return self._cache

    def get_validator(self) -> MatchValidator:
        return self._validator

    def get_percentile_ranking(self, percentile: Percentile) -> float:
        return self._percentiles[percentile]

    def get_percentile_ranking_for_game(self, game: ExcelGame) -> Percentile:
        if game.combined_rating <= self._percentiles[Percentile.P1]:
            return Percentile.P1
        if game.combined_rating <= self._percentiles[Percentile.P5]:
            return Percentile.P5
        if game.combined_rating <= self._percentiles[Percentile.P10]:
            return Percentile.P10
        if game.combined_rating <= self._percentiles[Percentile.P25]:
            return Percentile.P25
        if game.combined_rating <= self._percentiles[Percentile.MED]:
            return Percentile.MED
        if game.combined_rating <= self._percentiles[Percentile.P75]:
            return Percentile.P75
        if game.combined_rating <= self._percentiles[Percentile.P90]:
            return Percentile.P90
        if game.combined_rating <= self._percentiles[Percentile.P95]:
            return Percentile.P95
        return Percentile.P99

    @property
    def backloggd_client(self) -> BackloggdClient:
        return self._bcclient

    @property
    def giant_bomb_client(self) -> GiantBombClient:
        return self._gbclient

    @property
    def moby_games_client(self) -> MobyGamesClient:
        return self._mbclient

    def get_giant_bomb_titles_for_concept(self, concept_guid: str) -> Set[str]:
        cache_titles = self._gbcache.get(concept_guid)

        if cache_titles is not None:
            return cache_titles

        print(f"Cache miss for Giant Bomb concept GUID {concept_guid}")

        titles = set(
            g["name"]
            for g in asyncio.run(self._gbclient.concept(concept_guid))["results"][
                "games"
            ]
        )

        self._gbcache[concept_guid] = titles
        self._cache.write(self.__GIANT_BOMB_CACHE_FILE_NAME, self._gbcache)

        return titles

    def get_moby_games_titles_for_group(self, group_id: int) -> Set[str]:
        cache_titles = self._mbcache.get(group_id)

        if cache_titles is not None:
            return cache_titles

        print(f"Cache miss for Moby Games group ID {group_id}")

        games = self._get_moby_games_titles_internal(group_id)

        offset = 100
        while len(games) % 100 == 0:
            games.extend(self._get_moby_games_titles_internal(group_id, offset))
            offset += 100

        titles = set(mg.title for mg in games).union(
            set(alt.title for mg in games for alt in mg.alternate_titles)
        )

        self._mbcache[group_id] = titles
        self._cache.write(self.__MOBY_GAMES_CACHE_FILE_NAME, self._mbcache)

        return titles

    def _get_moby_games_titles_internal(self, group_id: int, offset: int = 0):
        return asyncio.run(self._mbclient.games(group_ids=[group_id], offset=offset))
