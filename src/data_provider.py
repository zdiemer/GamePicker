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
from match_validator import MatchValidator

from excel_backed_cache import ExcelBackedCache
from excel_filter import ExcelFilter


class Percentile(Enum):
    P25 = 0
    MED = 1
    P75 = 2
    P90 = 3
    P95 = 4
    P99 = 5


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

    def __init__(self, no_cache: bool = False):
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

                p25, med, p75, p90, p95, p99 = np.percentile(
                    [g.combined_rating for g in self._games],
                    [25, 50, 75, 90, 95, 99],
                )

                self._percentiles = {
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

        p25, med, p75, p90, p95, p99 = np.percentile(
            [g.combined_rating for g in self._games], [25, 50, 75, 90, 95, 99]
        )

        self._percentiles = {
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
