from __future__ import annotations

import asyncio
import copy
import datetime
import itertools
import json
import math
import os
import statistics
import random
import re
from difflib import SequenceMatcher, unified_diff
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import unidecode
from spellchecker import SpellChecker

from clients import (
    BackloggdClient,
    DatePart,
    GameyeClient,
    GiantBombClient,
    MobyGamesClient,
    RateLimit,
)

from excel_game import (
    ExcelGame,
    ExcelGenre,
    ExcelOwnedCondition,
    ExcelPlatform,
    ExcelRegion,
    FuzzyDateType,
    Playability,
    TranslationStatus,
)

from excel_loader import ExcelLoader

from logging_decorator import LoggingColor, LoggingDecorator
from match_validator import MatchValidator


import picker_output
from excel_backed_cache import ExcelBackedCache
from game_grouping import GameGrouping, GameGroups
from picked_game import PickedGame
from picker_constants import HANDHELD_PLATFORMS, NON_STREAMABLE_PLATFORMS
from picker_enums import PickerMode
from game_selector import GameSelector


class GamesPicker:
    _games: List[ExcelGame]
    _completed_games: List[ExcelGame]
    _games_on_order: List[ExcelGame]
    _unplayed_candidates: List[ExcelGame]
    _mode: PickerMode
    _played_games: List[ExcelGame]
    _validator: MatchValidator
    _bcclient: BackloggdClient
    _geclient: GameyeClient
    _gbclient: GiantBombClient
    _mbclient: MobyGamesClient
    _cache: ExcelBackedCache
    _mbcache: Dict[int, Set[str]]
    _gbcache: Dict[str, Set[str]]
    _loader: ExcelLoader
    _name_collisions: Dict[str, int]

    _p25: float
    _med: float
    _p75: float
    _p90: float
    _p95: float
    _p99: float

    __BASE_OUTPUT_PATH = "picker_out"
    __BASE_DROPBOX_FOLDER = "C:\\Users\\zachd\\Dropbox\\Video Game Lists"
    __EXCEL_SHEET_NAME = "Games Master List - Final.xlsx"
    __CACHE_FILE_NAME = "cache.pkl"

    CONDIITON_MAPPING = {
        ExcelOwnedCondition.COMPLETE: "CIB",
        ExcelOwnedCondition.GAME_ONLY: "Loose",
        ExcelOwnedCondition.GAME_AND_BOX_ONLY: "Loose",
    }

    def __init__(self, mode: PickerMode = PickerMode.ALL, no_cache: bool = False):
        self._mode = mode
        self._no_cache = no_cache
        self._cache = ExcelBackedCache()
        self._validator = MatchValidator()
        self._bcclient = BackloggdClient(self._validator)
        self._geclient = GameyeClient(self._validator)
        self._gbclient = GiantBombClient(self._validator)
        self._mbclient = MobyGamesClient(
            self._validator, rate_limit=RateLimit(1, DatePart.SECOND)
        )
        self._mbcache = {}
        self._gbcache = {}
        self._name_collisions = {}

        self._loader = ExcelLoader(self.__get_excel_file_name())

        if not no_cache:
            cache_data = self._cache.load(self.__CACHE_FILE_NAME)

            if cache_data is not None:
                (
                    self._games,
                    self._played_games,
                    self._unplayed_candidates,
                    self._completed_games,
                    self._games_on_order,
                ) = cache_data
                self._p25, self._med, self._p75, self._p90, self._p95, self._p99 = (
                    np.percentile(
                        [g.combined_rating for g in self._games],
                        [25, 50, 75, 90, 95, 99],
                    )
                )
                for g in self._games:
                    if g.game_platform_hash_id in self._name_collisions:
                        self._name_collisions[g.game_platform_hash_id] += 1
                    else:
                        self._name_collisions[g.game_platform_hash_id] = 1
                return

        self._games = self._loader.games

        self._p25, self._med, self._p75, self._p90, self._p95, self._p99 = (
            np.percentile(
                [g.combined_rating for g in self._games], [25, 50, 75, 90, 95, 99]
            )
        )

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
                lambda g: self.__filter_low_priority(g)
                and self.__filter_unplayable(g)
                and self.__filter_untranslated_text_heavy(g)
                and self.__filter_played(g)
                and self.__filter_unreleased(g),
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

    def __filter_unreleased(self, game: ExcelGame) -> bool:
        return (
            game.release_date is not None
            and game.release_date <= datetime.datetime.utcnow()
        )

    def __filter_played(self, game: ExcelGame) -> bool:
        return not game.completed

    def __filter_untranslated_text_heavy(self, game: ExcelGame) -> bool:
        return (
            game.translation is None
            or game.translation != TranslationStatus.NONE
            or game.genre
            not in (
                ExcelGenre.ACTION_RPG,
                ExcelGenre.ADVENTURE,
                ExcelGenre.CARD_GAME,
                ExcelGenre.COMPUTER_RPG,
                ExcelGenre.DUNGEON_CRAWLER,
                ExcelGenre.STRATEGY_RPG,
                ExcelGenre.TURN_BASED_RPG,
                ExcelGenre.VISUAL_NOVEL,
                ExcelGenre.ACTION_ADVENTURE,
                ExcelGenre.TURN_BASED_STRATEGY,
                ExcelGenre.TURN_BASED_TACTICS,
                ExcelGenre.STRATEGY,
                ExcelGenre.MMORPG,
                ExcelGenre.REAL_TIME_TACTICS,
                ExcelGenre.ROGUELIKE,
                ExcelGenre.SIMULATION,
                ExcelGenre.SURVIVAL_HORROR,
                ExcelGenre.TEXT_ADVENTURE,
                ExcelGenre.TRIVIA,
            )
        )

    def __filter_low_priority(self, game: ExcelGame) -> bool:
        return (game.priority or 0) > 1

    def __filter_unplayable(self, game: ExcelGame) -> bool:
        return game.playability == Playability.PLAYABLE

    def __filter_by_mode(self, game: ExcelGame) -> bool:
        if self._mode == PickerMode.HANDHELD:
            filtered_by_platform = game.platform in HANDHELD_PLATFORMS

            filtered_by_owned = filtered_by_platform and (
                game.platform
                not in (
                    ExcelPlatform.NINTENDO_3DS,
                    ExcelPlatform.DSIWARE,
                    ExcelPlatform.NINTENDO_SWITCH,
                )
                or game.owned
            )

            filtered_by_steam = filtered_by_owned and (
                game.platform != ExcelPlatform.PC
                or (
                    game.digital_platform == "Steam"
                    and not game.vr
                    and game.genre
                    not in (
                        ExcelGenre.REAL_TIME_STRATEGY,
                        ExcelGenre.FIRST_PERSON_SHOOTER,
                        ExcelGenre.TEXT_ADVENTURE,
                    )
                )
            )

            filtered_by_laserdisc = filtered_by_steam and (
                game.platform != ExcelPlatform.ARCADE
                or game.physical_media_format != "LaserDisc"
            )

            return filtered_by_laserdisc
        if self._mode == PickerMode.HIGH_PRIORITY:
            return (game.priority or 0) > 3 or game.combined_rating >= 0.8
        if self._mode == PickerMode.OWNED:
            return game.owned
        if self._mode == PickerMode.STREAMABLE:
            filtered_by_platform = game.platform not in NON_STREAMABLE_PLATFORMS

            filtered_by_owned = filtered_by_platform and game.platform not in (
                ExcelPlatform.NINTENDO_3DS,
                ExcelPlatform.NINTENDO_SWITCH,
                ExcelPlatform.NINTENDO_WII_U,
                ExcelPlatform.PLAYSTATION_3,
                ExcelPlatform.PLAYSTATION_VITA,
            )

            return filtered_by_owned
        return True

    def __get_game_with_metadata(
        self, game: ExcelGame, group_metadata: str
    ) -> ExcelGame:
        g_copy = copy.copy(game)
        g_copy.group_metadata = group_metadata
        return g_copy

    def __get_mobygames_for_group(self, group_id: int, offset: int = 0):
        return asyncio.run(self._mbclient.games(group_ids=[group_id], offset=offset))

    def __get_mobygames_titles(self, group_id: int) -> Set[str]:
        cache_titles = self._mbcache.get(group_id)

        if cache_titles is not None:
            return cache_titles

        games = self.__get_mobygames_for_group(group_id)

        offset = 100
        while len(games) % 100 == 0:
            games.extend(self.__get_mobygames_for_group(group_id, offset))
            offset += 100

        titles = set(mg.title for mg in games).union(
            set(alt.title for mg in games for alt in mg.alternate_titles)
        )

        self._mbcache[group_id] = titles

        return titles

    def __get_gb_titles_for_concept(self, concept_guid: str):
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

        return titles

    def __backloggd_top(self, games: List[ExcelGame]) -> List[ExcelGame]:
        pop_iter = self._bcclient.get_popular_games()

        popular = []
        i = 0
        pi = 0

        for g in pop_iter:
            upg = next(
                filter(
                    lambda _g: self._validator.titles_equal_normalized(g, _g.title),
                    games,
                ),
                None,
            )

            if upg is not None:
                upgc = copy.copy(upg)
                upgc.group_metadata = i
                popular.append(upgc)
                i += 1

            if len(popular) >= 50 or (pi / 50) > 10:
                break

        return popular

    def __best_companies_by_metacritic(self, games: List[ExcelGame]) -> List[ExcelGame]:
        by_developer = GameGrouping(lambda g: g.developer).get_groups(
            list(filter(lambda g: g.metacritic_rating is not None, games)),
        )

        by_publisher = GameGrouping(lambda g: g.publisher).get_groups(
            list(filter(lambda g: g.metacritic_rating is not None, games)),
        )

        combined = list(by_developer.items())
        combined.extend(by_publisher.items())

        by_company = {}

        for key, value in combined:
            if key in by_company:
                by_company[key] = by_company[key].union(set(value))
            else:
                by_company[key] = set(value)

        companies_to_remove = []

        for key, value in by_company.items():
            if len(value) < 5:
                companies_to_remove.append(key)

        for company in companies_to_remove:
            del by_company[company]

        company_ratings = GameGroups(by_company).with_agg(
            lambda gs: statistics.mean([g.game.metacritic_rating for g in gs]),
            inplace=False,
        )

        return list(
            set(
                self.__get_game_with_metadata(g.game, kvp[0])
                for kvp in sorted(
                    company_ratings.items(), key=lambda kvp: kvp[1], reverse=True
                )[:10]
                for g in by_company[kvp[0]]
            )
        )

    def __best_years_by_metacritic(self, games: List[ExcelGame]) -> List[ExcelGame]:
        by_year = GameGrouping(lambda g: g.release_year).get_groups(
            list(filter(lambda g: g.metacritic_rating is not None, games)),
        )

        years_to_remove = []

        for key, value in by_year.items():
            if len(value) < 5:
                years_to_remove.append(key)

        for year in years_to_remove:
            del by_year[year]

        year_ratings = by_year.with_agg(
            lambda gs: statistics.mean([g.game.metacritic_rating for g in gs]),
            inplace=False,
        )

        return [
            g.game
            for kvp in sorted(
                year_ratings.items(), key=lambda kvp: kvp[1], reverse=True
            )[:10]
            for g in by_year[kvp[0]]
        ]

    def __favorites(self, games: List[ExcelGame]) -> List[ExcelGame]:
        by_developer = (
            GameGrouping(lambda g: g.developer)
            .get_groups(self._played_games)
            .with_agg(lambda gs: statistics.mean(g.game.rating for g in gs))
        )

        by_publisher = (
            GameGrouping(lambda g: g.publisher)
            .get_groups(self._played_games)
            .with_agg(lambda gs: statistics.mean(g.game.rating for g in gs))
        )

        by_franchise = (
            GameGrouping(lambda g: g.franchise)
            .get_groups(
                list(filter(lambda g: g.franchise is not None, self._played_games))
            )
            .with_agg(lambda gs: statistics.mean(g.game.rating for g in gs))
        )

        favorite_developers = set(
            kvp[0]
            for kvp in sorted(
                by_developer.items(), key=lambda kvp: kvp[1], reverse=True
            )[:10]
        )

        favorite_publishers = set(
            kvp[0]
            for kvp in sorted(
                by_publisher.items(), key=lambda kvp: kvp[1], reverse=True
            )[:10]
        )

        favorite_franchises = set(
            kvp[0]
            for kvp in sorted(
                by_franchise.items(), key=lambda kvp: kvp[1], reverse=True
            )[:10]
        )

        unplayed_favorites = set()

        for g in games:
            if g.developer in favorite_developers:
                unplayed_favorites.add(
                    self.__get_game_with_metadata(g, f"Developer: {g.developer}")
                )
            if g.publisher in favorite_publishers:
                unplayed_favorites.add(
                    self.__get_game_with_metadata(g, f"Publisher: {g.publisher}")
                )
            if g.franchise in favorite_franchises:
                unplayed_favorites.add(
                    self.__get_game_with_metadata(g, f"Franchise: {g.franchise}")
                )

        return list(unplayed_favorites)

    def __franchise_playthroughs(self, _: List[ExcelGame]) -> List[ExcelGame]:
        by_franchise = GameGrouping(lambda g: g.franchise).get_groups(
            list(
                filter(
                    lambda g: g.franchise is not None
                    and self.__filter_by_mode(g)
                    and self.__filter_low_priority(g)
                    and self.__filter_unplayable(g)
                    and self.__filter_untranslated_text_heavy(g)
                    and self.__filter_played(g)
                    and self.__filter_unreleased(g),
                    self._games,
                )
            ),
        )

        by_franchise_played = GameGrouping(lambda g: g.franchise).get_groups(
            list(filter(lambda g: g.franchise is not None, self._played_games)),
        )

        next_up = []

        for franchise in by_franchise_played.keys():
            if franchise in by_franchise:
                next_up.extend(g.game for g in by_franchise[franchise])

        return next_up

    def __zero_percent(self, games: List[ExcelGame]) -> List[ExcelGame]:
        by_platform = GameGrouping().get_groups(self._played_games)
        by_genre = GameGrouping(lambda g: g.genre).get_groups(self._played_games)
        by_metacritic = GameGrouping(
            lambda g: f"{(g.metacritic_rating * 100) // 10 / 10:.0%}"
        ).get_groups(
            list(filter(lambda g: g.metacritic_rating is not None, self._played_games)),
        )
        by_game_faqs = GameGrouping(
            lambda g: f"{(g.gamefaqs_rating * 100) // 10 / 10:.0%}"
        ).get_groups(
            list(filter(lambda g: g.gamefaqs_rating is not None, self._played_games)),
        )
        by_year = GameGrouping(lambda g: g.release_year).get_groups(
            self._played_games,
        )

        zeroes = []

        for game in games:
            if game.platform not in by_platform:
                zeroes.append(
                    self.__get_game_with_metadata(game, f"Platform: {game.platform}")
                )
            if game.genre not in by_genre:
                zeroes.append(
                    self.__get_game_with_metadata(game, f"Genre: {game.genre}")
                )
            if (
                game.metacritic_rating is not None
                and f"{(game.metacritic_rating * 100) // 10 / 10:.0%}"
                not in by_metacritic
            ):
                zeroes.append(
                    self.__get_game_with_metadata(
                        game,
                        f"Metacritic Rating: {(game.metacritic_rating * 100) // 10 / 10:.0%}",
                    )
                )
            if (
                game.gamefaqs_rating is not None
                and f"{(game.gamefaqs_rating * 100) // 10 / 10:.0%}" not in by_game_faqs
            ):
                zeroes.append(
                    self.__get_game_with_metadata(
                        game,
                        f"GameFAQs Rating: {(game.gamefaqs_rating * 100) // 10 / 10:.0%}",
                    )
                )
            if game.release_year not in by_year:
                zeroes.append(
                    self.__get_game_with_metadata(
                        game, f"Release Year: {game.release_year}"
                    )
                )

        return zeroes

    async def __completed_values(self, games: List[ExcelGame]) -> List[ExcelGame]:
        priced_games = []

        print(f"Pricing {len(games)} games.")

        for game in games:
            if self._geclient.should_skip(game):
                continue

            if game.owned_condition is None:
                print(f"Skipped {game.full_name} due to missing condition.")
                game.group_metadata = None
                priced_games.append(game)
                continue

            matches = await self._geclient.match_game(game)

            if matches is not None and len(matches) == 1:
                if (
                    not matches[0].match_info
                    or not matches[0].match_info.get("price")
                    or not matches[0]
                    .match_info["price"]
                    .get(self.CONDIITON_MAPPING[game.owned_condition])
                ):
                    print(f"Skipping {game.full_name} due to no price info on Gameye.")
                    game.group_metadata = None
                    priced_games.append(game)
                    continue

                game.group_metadata = float(
                    matches[0].match_info["price"][
                        self.CONDIITON_MAPPING[game.owned_condition]
                    ]
                )

                if game.copies_owned is not None:
                    game.group_metadata *= game.copies_owned
                    game.title += f" ({game.copies_owned} copies owned)"

                print(
                    f"Found price for {game.full_name} - ${game.group_metadata / 100:,.2f}"
                )
                priced_games.append(game)
                continue

            if matches is not None and len(matches) > 1:
                print(f"Found multiple prices for {game.full_name}")
                game.group_metadata = None
                priced_games.append(game)

        return priced_games

    def __non_downloaded_games(self, games: List[ExcelGame]) -> List[ExcelGame]:
        by_platform = GameGrouping().get_groups(games)
        pattern = r"(\(.*\))|(\[.*\])|([vV]{1}[0-9]{1}\.[0-9]{1})|(_.*)|(, The)"
        non_downloaded = []

        for platform, p_games in by_platform.items():
            folders = []

            # Atari
            if platform == ExcelPlatform.ATARI_8_BIT:
                folders.append("E:\\Emulation\\Atari\\Atari 8-bit")
            if platform == ExcelPlatform.ATARI_2600:
                folders.append("E:\\Emulation\\Atari\\Atari 2600")
            if platform == ExcelPlatform.ATARI_5200:
                folders.append("E:\\Emulation\\Atari\\Atari 5200")
            if platform == ExcelPlatform.ATARI_7800:
                folders.append("E:\\Emulation\\Atari\\Atari 7800")
            if platform == ExcelPlatform.ATARI_JAGUAR:
                folders.append("E:\\Emulation\\Atari\\Atari Jaguar")
            if platform == ExcelPlatform.ATARI_JAGUAR_CD:
                folders.append("E:\\Emulation\\Atari\\Atari Jaguar CD")
            if platform == ExcelPlatform.ATARI_LYNX:
                folders.append("E:\\Emulation\\Atari\\Atari Lynx")
            if platform == ExcelPlatform.ATARI_ST:
                folders.append("E:\\Emulation\\Atari\\Atari ST")

            # Commodore
            if platform == ExcelPlatform.COMMODORE_64:
                folders.extend(
                    [
                        "E:\\Emulation\\Commodore\\Commodore 64",
                        "D:\\itch.io\\Commodore 64",
                    ]
                )
            if platform == ExcelPlatform.COMMODORE_AMIGA:
                folders.append("E:\\Emulation\\Commodore\\Commodore Amiga")
            if platform == ExcelPlatform.COMMODORE_AMIGA_CD32:
                folders.append("E:\\Emulation\\Commodore\\Commodore Amiga CD32")
            if platform == ExcelPlatform.COMMODORE_PLUS_4:
                folders.append("E:\\Emulation\\Commodore\\Commodore Plus 4")
            if platform == ExcelPlatform.COMMODORE_VIC_20:
                folders.append("E:\\Emulation\\Commodore\\Commodore VIC-20")

            # Microsoft
            if platform == ExcelPlatform.XBOX:
                folders.append("E:\\Emulation\\Microsoft\\Xbox")
            if platform == ExcelPlatform.XBOX_360:
                folders.append("E:\\Emulation\\Microsoft\\Xbox 360")

            # Nintendo
            if platform == ExcelPlatform.FAMICOM_DISK_SYSTEM:
                folders.append("E:\\Emulation\\Nintendo\\Famicom Disk System")
            if platform == ExcelPlatform.GAME_BOY:
                folders.append("E:\\Emulation\\Nintendo\\Game Boy")
            if platform == ExcelPlatform.GAME_BOY_ADVANCE:
                folders.append("E:\\Emulation\\Nintendo\\Game Boy Advance")
            if platform == ExcelPlatform.GAME_BOY_COLOR:
                folders.append("E:\\Emulation\\Nintendo\\Game Boy Color")
            if platform == ExcelPlatform.NINTENDO_GAMECUBE:
                folders.append("E:\\Emulation\\Nintendo\\GameCube")
            if platform == ExcelPlatform.NES:
                folders.extend(
                    [
                        "E:\\Emulation\\Nintendo\\NES\\Famicom",
                        "E:\\Emulation\\Nintendo\\NES\\Nintendo Entertainment System",
                        "D:\\itch.io\\NES",
                    ]
                )
            if platform == ExcelPlatform.NINTENDO_3DS:
                folders.append("E:\\Emulation\\Nintendo\\Nintendo 3DS")
            if platform == ExcelPlatform.NINTENDO_64:
                folders.append("E:\\Emulation\\Nintendo\\Nintendo 64")
            if platform == ExcelPlatform.NINTENDO_64DD:
                folders.append("E:\\Emulation\\Nintendo\\Nintendo 64DD")
            if platform == ExcelPlatform.NINTENDO_DS:
                folders.append("E:\\Emulation\\Nintendo\\Nintendo DS")
            if platform == ExcelPlatform.DSIWARE:
                folders.append("E:\\Emulation\\Nintendo\\Nintendo DS\\DSiWare")
            if platform == ExcelPlatform.NINTENDO_DSI:
                folders.append("E:\\Emulation\\Nintendo\\Nintendo DS\\Nintendo DSi")
            if platform == ExcelPlatform.NINTENDO_POKEMON_MINI:
                folders.append("E:\\Emulation\\Nintendo\\Nintendo Pokémon mini")
            if platform == ExcelPlatform.SNES:
                folders.extend(
                    [
                        "E:\\Emulation\\Nintendo\\SNES\\Nintendo Power",
                        "E:\\Emulation\\Nintendo\\SNES\\Super Famicom",
                        "E:\\Emulation\\Nintendo\\SNES\\Super Nintendo Entertainment System",
                    ]
                )
            if platform == ExcelPlatform.BS_X:
                folders.append("E:\\Emulation\\Nintendo\\SNES\\Satellaview")
            if platform == ExcelPlatform.VIRTUAL_BOY:
                folders.append("E:\\Emulation\\Nintendo\\Virtual Boy")
            if platform == ExcelPlatform.NINTENDO_WII:
                folders.append("E:\\Emulation\\Nintendo\\Wii")
            if platform == ExcelPlatform.WIIWARE:
                folders.append("E:\\Emulation\\Nintendo\\Wii\\WiiWare")
            if platform == ExcelPlatform.NINTENDO_WII_U:
                folders.append("E:\\Emulation\\Nintendo\\Wii U")

            # Other
            if platform == ExcelPlatform._3DO:
                folders.append("E:\\Emulation\\Other\\3DO")
            if platform == ExcelPlatform.ACORN_ARCHIMEDES:
                folders.append("E:\\Emulation\\Other\\Acorn Archimedes")
            if platform == ExcelPlatform.RISC_PC:
                folders.append("E:\\Emulation\\Other\\Acorn Archimedes")
            if platform == ExcelPlatform.ACORN_ELECTRON:
                folders.append("E:\\Emulation\\Other\\Acorn Electron")
            if platform == ExcelPlatform.AMSTRAD_CPC:
                folders.append("E:\\Emulation\\Other\\Amstrad CPC")
            if platform == ExcelPlatform.ANDROID:
                folders.extend(
                    ["E:\\Emulation\\Other\\Android", "D:\\itch.io\\Android"]
                )
            if platform == ExcelPlatform.APPLE_II:
                folders.append("E:\\Emulation\\Other\\Apple II")
            if platform == ExcelPlatform.ARCADE:
                folders.append("E:\\Emulation\\Other\\Arcade (Non-MAME)")
            if platform == ExcelPlatform.BBC_MICRO:
                folders.append("E:\\Emulation\\Other\\BBC Micro")
            if platform == ExcelPlatform.COLECOVISION:
                folders.append("E:\\Emulation\\Other\\ColecoVision")
            if platform == ExcelPlatform.DEDICATED_CONSOLE:
                folders.append("E:\\Emulation\\Other\\Dedicated Console")
            if platform == ExcelPlatform.EPOCH_SUPER_CASSETTE_VISION:
                folders.append("E:\\Emulation\\Other\\Epoch Super Cassette Vision")
            if platform == ExcelPlatform.FM_TOWNS:
                folders.append("E:\\Emulation\\Other\\FM Towns")
            if platform == ExcelPlatform.FM_7:
                folders.append("E:\\Emulation\\Other\\FM-7")
            if platform == ExcelPlatform.GAMEPARK_32:
                folders.append("E:\\Emulation\\Other\\GamePark 32")
            if platform == ExcelPlatform.INTELLIVISION:
                folders.append("E:\\Emulation\\Other\\Intellivision")
            if platform == ExcelPlatform.J2ME:
                folders.extend(
                    [
                        "E:\\Emulation\\Other\\J2ME",
                        "E:\\Emulation\\Other\\J2ME\\call-of-duty-java-collection_202012",
                    ]
                )
            if platform == ExcelPlatform.MSX:
                folders.append("E:\\Emulation\\Other\\MSX\\MSX")
            if platform == ExcelPlatform.MSX2:
                folders.append("E:\\Emulation\\Other\\MSX\\MSX2")
            if platform == ExcelPlatform.MSX_TURBO_R:
                folders.append("E:\\Emulation\\Other\\MSX\\MSX Turbo-R")
            if platform == ExcelPlatform.NEC_PC_8801:
                folders.append("E:\\Emulation\\Other\\NEC PC-8801")
            if platform == ExcelPlatform.NEC_PC_9801:
                folders.append("E:\\Emulation\\Other\\NEC PC-9801")
            if platform == ExcelPlatform.NEO_GEO_CD:
                folders.append("E:\\Emulation\\Other\\Neo-Geo CD")
            if platform == ExcelPlatform.NEO_GEO_POCKET:
                folders.append("E:\\Emulation\\Other\\Neo-Geo Pocket")
            if platform == ExcelPlatform.NEO_GEO_POCKET_COLOR:
                folders.append("E:\\Emulation\\Other\\Neo-Geo Pocket")
            if platform == ExcelPlatform.N_GAGE:
                folders.append("E:\\Emulation\\Other\\N-Gage")
            if platform == ExcelPlatform.N_GAGE_2_0:
                folders.append("E:\\Emulation\\Other\\N-Gage")
            if platform == ExcelPlatform.PC_FX:
                folders.append("E:\\Emulation\\Other\\PC-FX")
            if platform == ExcelPlatform.PHILIPS_CD_I:
                folders.append("E:\\Emulation\\Other\\Philips CD-i")
            if platform == ExcelPlatform.SHARP_X1:
                folders.append("E:\\Emulation\\Other\\Sharp X1")
            if platform == ExcelPlatform.SHARP_X68000:
                folders.append("E:\\Emulation\\Other\\Sharp X68000")
            if platform == ExcelPlatform.SUPERGRAFX:
                folders.append("E:\\Emulation\\Other\\SuperGrafx")
            if platform == ExcelPlatform.GAME_COM:
                folders.append("E:\\Emulation\\Other\\Tiger Game.com")
            if platform == ExcelPlatform.TRS_80_COLOR_COMPUTER:
                folders.append("E:\\Emulation\\Other\\TRS-80 Color Computer")
            if platform == ExcelPlatform.TURBOGRAFX_16:
                folders.append("E:\\Emulation\\Other\\TurboGrafx-16\\TurboGrafx-16")
            if platform == ExcelPlatform.TURBOGRAFX_CD:
                folders.append("E:\\Emulation\\Other\\TurboGrafx-16\\TurboGrafx-CD")
            if platform == ExcelPlatform.VECTREX:
                folders.append("E:\\Emulation\\Other\\Vectrex")
            if platform == ExcelPlatform.WATARA_SUPERVISION:
                folders.append("E:\\Emulation\\Other\\Watara SuperVision")
            if platform == ExcelPlatform.WONDERSWAN:
                folders.append("E:\\Emulation\\Other\\WonderSwan\\WonderSwan")
            if platform == ExcelPlatform.WONDERSWAN_COLOR:
                folders.append("E:\\Emulation\\Other\\WonderSwan\\WonderSwan Color")
            if platform == ExcelPlatform.ZEEBO:
                folders.append("E:\\Emulation\\Other\\Zeebo")
            if platform == ExcelPlatform.ZX_SPECTRUM:
                folders.append("E:\\Emulation\\Other\\ZX Spectrum")

            # Sega
            if platform == ExcelPlatform.SEGA_DREAMCAST:
                folders.append("E:\\Emulation\\Sega\\Dreamcast")
            if platform == ExcelPlatform.SEGA_GAME_GEAR:
                folders.append("E:\\Emulation\\Sega\\Game Gear")
            if platform == ExcelPlatform.SEGA_SATURN:
                folders.append("E:\\Emulation\\Sega\\Saturn")
            if platform == ExcelPlatform.SEGA_GENESIS:
                folders.extend(
                    [
                        "E:\\Emulation\\Sega\\Sega Genesis\\Genesis",
                        "D:\\itch.io\\Genesis",
                    ]
                )
            if platform == ExcelPlatform.SEGA_32X:
                folders.append("E:\\Emulation\\Sega\\Sega Genesis\\Sega 32X")
            if platform == ExcelPlatform.SEGA_CD:
                folders.append("E:\\Emulation\\Sega\\Sega Genesis\\Sega CD")
            if platform == ExcelPlatform.SEGA_MASTER_SYSTEM:
                folders.append("E:\\Emulation\\Sega\\Sega Master System")
            if platform == ExcelPlatform.SEGA_SG_1000:
                folders.append("E:\\Emulation\\Sega\\Sega SG-1000")

            # Sony
            if platform == ExcelPlatform.PLAYSTATION:
                folders.append("E:\\Emulation\\Sony\\PlayStation")
            if platform == ExcelPlatform.PLAYSTATION_2:
                folders.append("E:\\Emulation\\Sony\\PlayStation 2")
            if platform == ExcelPlatform.PLAYSTATION_3:
                folders.append("E:\\Emulation\\Sony\\PlayStation 3")
            if platform == ExcelPlatform.PLAYSTATION_PORTABLE:
                folders.append("E:\\Emulation\\Sony\\PlayStation Portable")
            if platform == ExcelPlatform.PLAYSTATION_VITA:
                folders.append("E:\\Emulation\\Sony\\PlayStation Vita")

            # PC

            if platform == ExcelPlatform.PC:
                folders.extend(
                    [
                        "E:\\Emulation\\Other\\MS-DOS",
                        "D:\\Abandonware",
                        "D:\\DRM Free",
                        "D:\\Freeware",
                        "D:\\itch.io\\PC",
                    ]
                )

            # itch.io
            if platform == ExcelPlatform.PLAYDATE:
                folders.append("D:\\itch.io\\Playdate")

            if any(folders):
                downloaded = set([])
                for folder in folders:
                    for _, subfolders, files in os.walk(folder):
                        for file in files:
                            if file == "desktop.ini":
                                continue
                            file_name = (
                                re.sub(pattern, "", Path(file).stem)
                                .strip()
                                .replace(" - ", ": ")
                            )
                            downloaded.add(file_name)
                        for subfolder in subfolders:
                            folder_name = (
                                re.sub(pattern, "", subfolder)
                                .strip()
                                .replace(" - ", ": ")
                            )
                            downloaded.add(folder_name)
                        break

                for game in p_games:
                    should_check = (
                        game.game.platform == ExcelPlatform.PC
                        and (
                            not game.game.notes
                            or game.game.notes in ("Freeware", "DRM Free", "itch.io")
                        )
                    ) or game.game.notes == "itch.io"
                    if game.game.owned and not should_check:
                        continue

                    matched = False

                    for d_game in downloaded:
                        if self._validator.titles_equal_fuzzy(
                            d_game, game.game.normal_title
                        ):
                            matched = True
                            break

                    if not matched:
                        non_downloaded.append(game.game)
            else:
                non_downloaded.extend(
                    list(filter(lambda g: not g.owned, [p.game for p in p_games]))
                )

        return non_downloaded

    def __misspellings(self, games: List[ExcelGame]) -> List[ExcelGame]:
        misspelled = []
        checker = SpellChecker()
        checker.word_frequency.load_text_file("dictionary.txt")

        def get_words(t: str) -> Set[str]:
            words = t.split()
            output_words = set()

            for word in words:
                word = re.sub(r"[^A-Za-z0-9\s]", "", word).strip()
                compound = re.findall(r"[A-Z][^A-Z]*", word)

                if any(compound):
                    if not any(checker.unknown([word])):
                        continue
                    output_words = output_words.union(set(compound))
                    continue

                output_words.add(word)

            return output_words.difference(set([""]))

        all_misspelled_words = set([])

        for game in games:
            title_words = get_words(game.title)
            misspelled_words = checker.unknown(title_words)
            all_misspelled_words = all_misspelled_words.union(set(misspelled_words))

            for word in misspelled_words:
                if checker.correction(word) is not None:
                    misspelled.append(game)
                    break

        return misspelled

    def __sheet_validations(self, games: List[ExcelGame]) -> List[ExcelGame]:
        invalid_games: List[ExcelGame] = []
        all_titles: Set[str] = set([])

        for game in games:
            all_titles.add(game.title)

            # Owned Physical Games Missing Condition
            if (
                game.owned
                and game.owned_format in ("Physical", "Both")
                and game.owned_condition is None
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Missing Condition"
                invalid_games.append(g_copy)

            # Owned Games Missing Format
            if game.owned and (game.owned_format is None or game.owned == ""):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Missing Format"
                invalid_games.append(g_copy)

            # Completed Games with Lingering Metadata
            if game.completed and (
                game.estimated_playtime is not None or game.priority is not None
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Lingering Metadata"
                invalid_games.append(g_copy)

            # Wishlisted and Owned
            if game.owned and game.wishlisted:
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Wishlisted and Owned"
                invalid_games.append(g_copy)

            # Missing Rating
            if game.completed and game.rating is None:
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Missing Rating"
                invalid_games.append(g_copy)

            # Owned PC Game Missing Subplatform
            if (
                game.owned
                and game.platform == ExcelPlatform.PC
                and (game.notes is None or game.notes == "")
            ):
                print(f"{game.title} is missing PC subplatform")
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Missing PC Subplatform"
                invalid_games.append(g_copy)

            # Unowned With Ownership Metadata
            if not game.owned and (
                game.owned_condition is not None
                or (game.date_purchased is not None and game.date_purchased != "")
                or (game.purchase_price is not None and game.purchase_price != "")
                or (game.owned_format is not None and game.owned_format != "")
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Unowned With Ownership Metadata"
                invalid_games.append(g_copy)

            # Browser Based Games Without Links
            if (
                not game.completed
                and game.platform == ExcelPlatform.BROWSER
                and game.notes
                not in (
                    "Link",
                    "itch.io",
                )
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Browser Games Without Links"
                invalid_games.append(g_copy)

            # Missing Translation Info
            if (
                game.release_region
                not in (ExcelRegion.EUROPE, ExcelRegion.NORTH_AMERICA)
                and game.translation is None
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Missing Translation Info"
                invalid_games.append(g_copy)

            # Estimated Time Not Multiple of 0.5
            if (
                game.estimated_playtime is not None
                and game.estimated_playtime > 1
                and game.estimated_playtime
                != 0.5 * round(game.estimated_playtime / 0.5)
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Estimated Playtime Using Incorrect Multiple"
                invalid_games.append(g_copy)

            # Trailing Whitespace
            if (
                game.title != game.title.strip()
                or game.publisher != game.publisher.strip()
                or game.developer != game.developer.strip()
                or (
                    game.franchise is not None
                    and game.franchise != game.franchise.strip()
                )
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Trailing Whitespace"
                invalid_games.append(g_copy)

            double_space_re = r"[ ]{2,}"

            # Double Spaces
            if (
                re.search(double_space_re, game.title) is not None
                or re.search(double_space_re, game.publisher) is not None
                or re.search(double_space_re, game.developer) is not None
                or (
                    game.franchise is not None
                    and re.search(double_space_re, game.franchise) is not None
                )
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Double Spaces"
                invalid_games.append(g_copy)

        games_dict = {g.hash_id: g for g in self._games}

        def round_to_2(num: float) -> float:
            return float(f"{num:,.2f}")

        def to_percent(num: float) -> int:
            return round(num * 100)

        for game in self._completed_games:
            # Collection Title Missing from Main Sheet
            if (
                game.collection is not None
                and game.collection != ""
                and game.collection not in all_titles
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Completed: Collection Mismatch"
                invalid_games.append(g_copy)

            # Typo in Notes
            if game.notes is not None and game.notes != "":
                pass

            if game.hash_id in games_dict:
                # Rating Mismatch
                if to_percent(game.rating) != to_percent(
                    games_dict[game.hash_id].rating or 0
                ):
                    g_copy = copy.copy(game)
                    g_copy.group_metadata = "Completed: Rating Mismatch"
                    invalid_games.append(g_copy)

                # Playtime Mismatch
                if round_to_2(game.completion_time or 0) != round_to_2(
                    games_dict[game.hash_id].completion_time or 0
                ):
                    g_copy = copy.copy(game)
                    g_copy.group_metadata = "Completed: Completion Time Mismatch"
                    invalid_games.append(g_copy)

                # Completed Date Mismatch
                if game.date_completed != games_dict[game.hash_id].date_completed:
                    g_copy = copy.copy(game)
                    g_copy.group_metadata = "Completed: Completed Date Mismatch"
                    invalid_games.append(g_copy)

                # Missing VR Metadata
                if game.played_in_vr and not games_dict[game.hash_id].vr:
                    g_copy = copy.copy(game)
                    g_copy.group_metadata = "Completed: VR Metadata Mismatch"
                    invalid_games.append(g_copy)

        order_hash_dict = {g.game_order_hash_id: g for g in self._games}

        for game in self._games_on_order:
            # Estimated Release Passed
            if (
                game.estimated_release is not None
                and game.estimated_release < datetime.datetime.now()
            ):
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Games on Order: Past Estimated Release"
                invalid_games.append(g_copy)

            # Games Added to Main Sheet but Not Removed from Games on Order
            if game.game_order_hash_id in order_hash_dict:
                g_copy = copy.copy(game)
                g_copy.group_metadata = "Games on Order: Not Removed From Order Sheet"
                invalid_games.append(g_copy)

        merged_games, errors = self._loader.merge()

        for error in errors:
            e_game, msg = error
            g_copy = copy.copy(e_game)
            g_copy.group_metadata = msg
            invalid_games.append(g_copy)

        for game in merged_games:
            if any(game.child_games) and game.hash_id in games_dict:
                # Collection's Total Playtime Doesn't Match Individual Entries
                if round_to_2(
                    sum(g.completion_time or 0 for g in game.child_games)
                ) != (round_to_2(games_dict[game.hash_id].completion_time or 0)):
                    g_copy = copy.copy(game)
                    g_copy.group_metadata = (
                        "Completed: Collection Completion Time Mismatch"
                    )
                    invalid_games.append(g_copy)

                # Collection's Rating Doesn't Match Individual Entries' Average
                if to_percent(
                    statistics.mean(g.rating for g in game.child_games)
                ) != to_percent(games_dict[game.hash_id].rating or 0):
                    g_copy = copy.copy(game)
                    g_copy.group_metadata = "Completed: Collection Rating Mismatch"
                    invalid_games.append(g_copy)

                # Collection's Completed Date Doesn't Match Individual Entries' Max
                if (
                    games_dict[game.hash_id].completed
                    and any(
                        filter(lambda g: g.date_completed is not None, game.child_games)
                    )
                    and games_dict[game.hash_id].date_completed
                    != max(
                        g.date_completed
                        for g in filter(
                            lambda _g: _g.date_completed is not None, game.child_games
                        )
                    )
                ):
                    g_copy = copy.copy(game)
                    g_copy.group_metadata = (
                        "Completed: Collection Completed Date Mismatch"
                    )
                    invalid_games.append(g_copy)

        return invalid_games

    def __incomplete_collections(self, _: List[ExcelGame]) -> List[ExcelGame]:
        games, _ = self._loader.merge()

        incomplete_collections: List[ExcelGame] = []

        for g in games:
            if any(g.child_games) and not g.completed:
                incomplete_collections.append(g)

        return incomplete_collections

    def __coop_games(self, games: List[ExcelGame]) -> List[ExcelGame]:
        game_master_output_folder = "D:\\Code\\GameMaster\\output\\cooptimus"
        coop_games = {}
        output = []

        for root, _, files in os.walk(game_master_output_folder):
            for file in files:
                if not file.startswith("matches-"):
                    continue

                with open(f"{root}/{file}", "r", encoding="utf-8") as f:
                    coop_games.update(json.loads(f.read()))

        for game in games:
            if game.hash_id in coop_games:
                game.group_metadata = coop_games[game.hash_id]["match_info"]
                output.append(game)

        return output

    def __cleanup(self):
        files_to_remove = []
        expected_files = []
        expected_cache_files = []

        cache_folder = f"{GameSelector.CACHE_FOLDER}\\{self._mode.name.lower()}"

        for selector in self.get_selectors():
            expected_files.append(selector.get_output_file_name())
            expected_cache_files.append(selector.get_cache_file_name())

        for root, _, files in os.walk(picker_output.get_output_path(self._mode)):
            for file in files:
                if file not in expected_files:
                    files_to_remove.append(os.path.join(root, file))
            break

        for root, _, files in os.walk(cache_folder):
            for file in files:
                if file not in expected_cache_files:
                    files_to_remove.append(os.path.join(root, file))
            break

        for file in files_to_remove:
            os.remove(file)
            print(f"Cleaned up {file}")

    def get_selectors(self) -> List[GameSelector]:
        platform_progress: Dict[ExcelPlatform, int] = {}
        total_platform: Dict[ExcelPlatform, int] = {}

        def get_or_set(
            d: Dict[ExcelPlatform, int], plat: ExcelPlatform, _all: List[ExcelGame]
        ) -> int:
            val = d.get(plat)

            if val is not None:
                return val

            d[plat] = len(list(filter(lambda g: g.platform == plat, _all)))

            return d[plat]

        selectors = [
            GameSelector(
                _filter=lambda g: g.genre == ExcelGenre._3D_PLATFORMER,
                name="3D Platformers",
            ),
            GameSelector(
                _filter=lambda g: g.release_year > 2005,
                name="AAA Games",
                grouping=GameGrouping(
                    lambda g: g.publisher,
                    _filter=lambda kvp: len(kvp[1]) / len(self._games) >= 0.005,
                ),
                description="Criteria: Publisher has published >= 0.5% of all games.",
            ),
            GameSelector(
                lambda gs: sorted(
                    gs,
                    key=lambda game: game.normal_title,
                ),
                name="Alphabetical",
                grouping=GameGrouping(
                    lambda g: (
                        g.normal_title[0].capitalize()
                        if g.normal_title[0].isalpha()
                        else "#" if g.normal_title[0].isdigit() else "?"
                    )
                ),
            ),
            GameSelector(
                custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
                sort=lambda g: g.game.combined_rating,
                reverse_sort=True,
                include_platform=False,
                name="Best By Platform",
                grouping=GameGrouping(take=10),
            ),
            GameSelector(
                grouping=GameGrouping(lambda g: g.release_year, reverse=True, take=10),
                custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
                sort=lambda g: g.game.combined_rating,
                reverse_sort=True,
                name="Best By Year",
            ),
            GameSelector(
                self.__best_companies_by_metacritic,
                grouping=GameGrouping(
                    lambda g: g.group_metadata,
                    reverse=True,
                    sort=lambda kvp: (
                        statistics.mean(g.game.metacritic_rating for g in kvp[1]),
                        kvp[0],
                    ),
                    get_group_name=lambda kvp: f"{kvp[0]} ({len(kvp[1])}) [{statistics.mean(g.game.metacritic_rating for g in kvp[1]):.0%}]",
                ),
                sort=lambda g: (g.game.metacritic_rating, g.game.normal_title),
                reverse_sort=True,
                custom_suffix=lambda g: f" - {g.metacritic_rating:.0%}",
                include_in_picks=False,
            ),
            GameSelector(
                self.__best_years_by_metacritic,
                grouping=GameGrouping(
                    lambda g: g.release_year,
                    reverse=True,
                    sort=lambda kvp: statistics.mean(
                        g.game.metacritic_rating for g in kvp[1]
                    ),
                    get_group_name=lambda kvp: f"{kvp[0]} ({len(kvp[1])}) [{statistics.mean(g.game.metacritic_rating for g in kvp[1]):.0%}]",
                ),
                sort=lambda g: g.game.metacritic_rating,
                reverse_sort=True,
                custom_suffix=lambda g: f" - {g.metacritic_rating:.0%}",
                include_in_picks=False,
            ),
            GameSelector(
                _filter=lambda game: 1 <= (game.estimated_playtime or 0) < 5,
                name="Between 1 and 5 Hours",
            ),
            GameSelector(
                _filter=lambda game: 5 <= (game.estimated_playtime or 0) < 10,
                name="Between 5 and 10 Hours",
            ),
            GameSelector(
                _filter=lambda g: 10 < (g.estimated_playtime or 0) <= 20,
                name="Between 10 and 20 Hours",
            ),
            GameSelector(
                _filter=lambda g: 20 < (g.estimated_playtime or 0) <= 30,
                name="Between 20 and 30 Hours",
            ),
            GameSelector(
                _filter=lambda g: (g.estimated_playtime or 0) > 30,
                name="Greater Than 30 Hours",
            ),
            GameSelector(
                _filter=lambda g: g.estimated_playtime is None,
                name="No Estimated Playtime",
            ),
            GameSelector(
                _filter=lambda game: game.genre == ExcelGenre.BEAT_EM_UP,
                name="Beat 'em Ups",
            ),
            GameSelector(
                _filter=lambda game: game.genre == ExcelGenre.RUN_AND_GUN,
                name="Run and Gun",
            ),
            GameSelector(
                _filter=lambda game: game.genre == ExcelGenre.HACK_AND_SLASH,
                name="Hack-and-Slash",
            ),
            GameSelector(
                _filter=lambda g: g.release_date.month == 4 and g.release_date.day == 5,
                name="Birthday Games",
                custom_suffix=lambda g: f" [{g.release_year}]",
            ),
            GameSelector(
                _filter=lambda game: game.genre == ExcelGenre.FIRST_PERSON_SHOOTER,
                name="Boomer Shooters",
            ),
            GameSelector(
                _filter=lambda game: game.genre == ExcelGenre.FIGHTING,
                name="Fighting Games",
            ),
            GameSelector(
                _filter=lambda game: game.genre == ExcelGenre.ACTION_ADVENTURE,
                name="Action Adventure Games",
            ),
            GameSelector(
                _filter=lambda game: game.genre
                in (ExcelGenre.ADVENTURE, ExcelGenre.TEXT_ADVENTURE),
                name="Point and Click Games",
            ),
            GameSelector(
                _filter=lambda game: game.genre
                in (
                    ExcelGenre.FLIGHT_SIMULATION,
                    ExcelGenre.RACING,
                    ExcelGenre.SPACE_COMBAT,
                    ExcelGenre.VEHICULAR_COMBAT,
                ),
                name="Vehicle Based Games",
            ),
            GameSelector(
                _filter=lambda game: game.genre
                in (
                    ExcelGenre.ACTION,
                    ExcelGenre.ARCADE,
                    ExcelGenre.BOARD_GAME,
                    ExcelGenre.CARD_GAME,
                    ExcelGenre.EDUCATIONAL,
                    ExcelGenre.EXPERIMENTAL,
                    ExcelGenre.HIDDEN_OBJECT,
                    ExcelGenre.PINBALL,
                    ExcelGenre.RHYTHM,
                    ExcelGenre.SPORTS,
                    ExcelGenre.SURVIVAL,
                    ExcelGenre.TOWER_DEFENSE,
                ),
                name="Offbeat Genre Games",
            ),
            GameSelector(
                _filter=lambda game: game.genre
                in (
                    ExcelGenre.PUZZLE,
                    ExcelGenre.PUZZLE_ACTION,
                    ExcelGenre.FIRST_PERSON_PUZZLE,
                ),
                name="Puzzle Games",
            ),
            GameSelector(
                _filter=lambda g: any(
                    self._validator.titles_equal_normalized(g.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-6735")
                ),
                name="Cyberpunk",
                skip_unless_specified=True,
            ),
            GameSelector(
                _filter=lambda g: any(
                    self._validator.titles_equal_normalized(g.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-5700")
                ),
                name="Immersive Sims",
                skip_unless_specified=True,
            ),
            GameSelector(_filter=lambda game: game.dlc, name="DLCs"),
            GameSelector(
                self.__favorites,
                grouping=GameGrouping(
                    lambda g: f'{g.group_metadata.split(":")[0]}s',
                    subgroupings=[
                        GameGrouping(lambda g: g.group_metadata.split(":")[1].strip())
                    ],
                ),
            ),
            GameSelector(
                self.__franchise_playthroughs,
                grouping=GameGrouping(
                    lambda g: g.franchise,
                    progress_indicator=lambda kvp: (
                        len(
                            list(
                                filter(
                                    lambda g: g.franchise == kvp[0], self._played_games
                                )
                            )
                        ),
                        len(
                            list(
                                filter(
                                    lambda g: g.franchise == kvp[0],
                                    self._played_games + self._unplayed_candidates,
                                )
                            )
                        ),
                    ),
                ),
                sort=lambda g: g.game.release_date,
                _filter=lambda g: g.franchise is not None,
                include_in_picks=False,
            ),
            GameSelector(
                name="Franchise Playthrough Contenders",
                grouping=GameGrouping(
                    lambda g: g.franchise,
                    progress_indicator=lambda kvp: (
                        len(
                            list(
                                filter(
                                    lambda g: g.franchise == kvp[0], self._played_games
                                )
                            )
                        ),
                        len(
                            list(
                                filter(
                                    lambda g: g.franchise == kvp[0],
                                    self._played_games + self._unplayed_candidates,
                                )
                            )
                        ),
                    ),
                ),
                sort=lambda g: g.game.release_date,
                _filter=lambda g: g.franchise
                in (
                    "Final Fantasy",
                    "Final Fantasy Tactics",
                    "Chocobo",
                    "Mana",
                    "SaGa",
                    "Dragon Quest",
                    "Megami Tensei",
                    "Red Faction",
                    "Castlevania",
                    "Kirby",
                    "Command & Conquer",
                    "The Elder Scrolls",
                    "Splinter Cell",
                    "Alone in the Dark",
                    "Silent Hill",
                    "The Darkness",
                    "Resident Evil",
                    "Turok",
                    "The Witcher",
                    "Halo",
                    "Infamous",
                    "Uncharted",
                    "Dead Island",
                    "Dead Rising",
                    "Deus Ex",
                    "Metal Gear",
                    "King's Field",
                    "Armored Core",
                    "Shadow Tower",
                    "Echo Night",
                    "Lost Kingdoms",
                    "Otogi",
                    "Souls",
                    "Yakuza",
                    "Ys",
                    "Xeno",
                    "Far Cry",
                    "Metroid",
                    "Call of Duty",
                    "Ace Attorney",
                    "Professor Layton",
                    "Advance Wars",
                    "Assassin's Creed",
                    "Star Ocean",
                    "Fire Emblem",
                    "Tales",
                    "Shining",
                    "Phantasy Star",
                    "The Legend of Heroes",
                    "Suikoden",
                    "Breath of Fire",
                    "Wild Arms",
                    "Arc the Lad",
                    "Grandia",
                    "Hyperdimension Neptunia",
                    "Ar tonelico",
                    "Final Fantasy Crystal Chronicles",
                    "Atelier",
                    "Kingdom Hearts",
                    "Lunar",
                    "Disgaea",
                    "Etrian Odyssey",
                    "Ogre Battle",
                    "Picross",
                    "Genkai Tokki",
                    "Parasite Eve",
                    "Summon Night",
                    "Mario RPG",
                    "Mario & Luigi",
                    "Paper Mario",
                    "Mario",
                    "The Legend of Zelda",
                    "Sonic the Hedgehog",
                    "Pikmin",
                    "Mega Man",
                    "Mega Man X",
                    "Mega Man Zero",
                    "Mega Man Battle Network",
                    "Mega Man Legends",
                    "Pokémon",
                    "Pokémon Ranger",
                    "Pokémon Mystery Dungeon",
                    "Jak and Daxter",
                    "Ratchet & Clank",
                    "Resistance",
                    "Spyro the Dragon",
                    "Crash Bandicoot",
                    "Sly Cooper",
                    "Killzone",
                    "Chibi-Robo",
                    "Grand Theft Auto",
                ),
            ),
            GameSelector(
                _filter=lambda game: game.notes is not None
                and game.notes.strip() == "Freeware",
                include_in_picks=False,
                name="Freeware",
            ),
            GameSelector(
                _filter=lambda game: game.developer.strip() == "FromSoftware"
                or game.publisher.strip() == "FromSoftware",
                name="FromSoftware",
            ),
            GameSelector(
                _filter=lambda game: game.genre == ExcelGenre.SURVIVAL_HORROR
                or any(
                    self._validator.titles_equal_normalized(game.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-4801")
                )
                or any(
                    self._validator.titles_equal_normalized(game.title, mg)
                    for mg in self.__get_mobygames_titles(4822)
                ),
                name="Horror Games",
                skip_unless_specified=True,
            ),
            GameSelector(
                _filter=lambda game: game.genre
                in (
                    ExcelGenre.ACTION_RPG,
                    ExcelGenre.COMPUTER_RPG,
                    ExcelGenre.TURN_BASED_RPG,
                    ExcelGenre.STRATEGY_RPG,
                    ExcelGenre.DUNGEON_CRAWLER,
                    ExcelGenre.MMORPG,
                ),
                name="JRPG",
            ),
            GameSelector(
                _filter=lambda g: g.estimated_playtime is not None,
                sort=lambda g: g.game.estimated_playtime,
                reverse_sort=True,
                include_platform=False,
                name="Longest Games",
                grouping=GameGrouping(take=10),
            ),
            GameSelector(
                _filter=lambda g: (
                    (g.metacritic_rating and g.metacritic_rating >= 0.8)
                    or (g.gamefaqs_rating and g.gamefaqs_rating >= 0.8)
                )
                and g.priority > 3
                and g.release_year >= 2009,
                grouping=GameGrouping(
                    lambda g: g.developer,
                    _filter=lambda kvp: len(kvp[1]) / len(self._games) < 0.0005
                    and any(pg.game.publisher == kvp[0] for pg in kvp[1]),
                ),
                name="Major Indie Games",
            ),
            GameSelector(
                _filter=lambda game: game.genre == ExcelGenre.METROIDVANIA,
                name="Metroidvania",
            ),
            GameSelector(
                _filter=lambda g: (g.estimated_playtime or 0) > 30,
                name="More Than 30 Hours",
            ),
            GameSelector(
                _filter=lambda g: g.platform == ExcelPlatform.PC
                and g.owned
                and g.digital_platform is not None
                and g.digital_platform != "Steam",
                name="Non-Steam",
                grouping=GameGrouping(lambda g: g.notes),
                include_platform=False,
                include_in_picks=False,
            ),
            GameSelector(
                _filter=lambda game: game.gamefaqs_rating is None
                and game.metacritic_rating is None,
                name="Obscure Games",
            ),
            GameSelector(
                _filter=lambda g: "san francisco" in g.normal_title
                or any(
                    self._validator.titles_equal_normalized(g.title, mg)
                    for mg in self.__get_mobygames_titles(10594)
                ),
                name="San Francisco Games",
                skip_unless_specified=True,
            ),
            GameSelector(
                grouping=GameGrouping(
                    lambda g: g.title, _filter=lambda kvp: len(kvp[1]) > 1
                ),
                include_in_picks=False,
                name="Potential Duplicates",
                run_on_modes=set([PickerMode.ALL]),
            ),
            GameSelector(
                _filter=lambda game: game.genre
                in (
                    ExcelGenre.SCROLLING_SHOOTER,
                    ExcelGenre.SHOOTER,
                    ExcelGenre.TWIN_STICK_SHOOTER,
                ),
                name="Shmups",
            ),
            GameSelector(
                _filter=lambda g: g.estimated_playtime is not None,
                sort=lambda g: g.game.estimated_playtime,
                name="Shortest Games",
                include_platform=False,
                grouping=GameGrouping(take=10),
            ),
            GameSelector(
                _filter=lambda g: g.estimated_playtime is not None,
                sort=lambda g: g.game.estimated_playtime,
                name="Shortest Overall",
                grouping=GameGrouping(lambda _: "Shortest", take=100),
            ),
            GameSelector(
                _filter=lambda game: game.estimated_playtime is not None
                and game.genre
                not in (ExcelGenre.FIGHTING, ExcelGenre.SCROLLING_SHOOTER),
                sort=lambda g: g.game.estimated_playtime,
                name="Shortest Overall - Uncommon Genre",
                grouping=GameGrouping(lambda _: "Shortest", take=100),
            ),
            GameSelector(
                _filter=lambda game: game.subscription_service is not None,
                name="Subscriptions",
                grouping=GameGrouping(
                    lambda g: g.subscription_service,
                    subgroupings=[GameGrouping(lambda g: g.platform)],
                ),
                include_platform=False,
                include_in_picks=False,
            ),
            GameSelector(
                lambda games: [
                    g.game
                    for pgs in GameGrouping().get_groups(games).values()
                    for g in filter(lambda pg: pg.highest_priority, pgs)
                ],
                grouping=GameGrouping(
                    lambda g: f"{(g.combined_rating * 100) // 10 / 10:.0%}",
                    reverse=True,
                ),
                sort=lambda g: g.game.combined_rating,
                reverse_sort=True,
                custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
                name="Top Games",
            ),
            GameSelector(
                _filter=lambda game: game.estimated_playtime is not None
                and game.estimated_playtime < 1,
                name="Under 1 Hour",
            ),
            GameSelector(
                _filter=lambda game: game.estimated_playtime is not None
                and game.estimated_playtime < 1
                and game.genre
                not in (ExcelGenre.FIGHTING, ExcelGenre.SCROLLING_SHOOTER),
                name="Under 1 Hour - Uncommon Genre",
                grouping=GameGrouping(lambda g: g.genre),
            ),
            GameSelector(
                _filter=lambda game: game.owned
                and game.date_purchased is not None
                and (game.purchase_price or 0) > 0,
                name="Unplayed Purchases",
                grouping=GameGrouping(
                    lambda g: datetime.datetime(
                        g.date_purchased.year, g.date_purchased.month, 1
                    ),
                    reverse=True,
                    get_group_name=lambda kvp: f'{kvp[0].strftime("%b, %Y")} (${sum(g.game.purchase_price for g in kvp[1]):.2f})',
                ),
                custom_prefix=lambda g: f"{g.date_purchased.strftime('%m/%d: ')}",
                custom_suffix=lambda g: f" - ${g.purchase_price:0.2f}",
                sort=lambda g: (g.game.date_purchased, g.game.normal_title),
                reverse_sort=True,
            ),
            GameSelector(
                _filter=lambda game: game.completed
                and game.owned
                and game.date_purchased is not None
                and (game.purchase_price or 0) > 0,
                name="Played Purchases",
                grouping=GameGrouping(
                    lambda g: datetime.datetime(
                        g.date_purchased.year, g.date_purchased.month, 1
                    ),
                    reverse=True,
                    get_group_name=lambda kvp: f'{kvp[0].strftime("%b, %Y")} (${sum(g.game.purchase_price for g in kvp[1]):.2f})',
                ),
                custom_prefix=lambda g: f"{g.date_purchased.strftime('%m/%d: ')}",
                custom_suffix=lambda g: f" - ${g.purchase_price:0.2f}",
                sort=lambda g: (g.game.date_purchased, g.game.normal_title),
                reverse_sort=True,
                games=self._games,
                run_on_modes=set([PickerMode.ALL]),
            ),
            GameSelector(
                _filter=lambda game: game.combined_rating < 0.4,
                name="Very Bad Games",
                custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
                sort=lambda g: g.game.combined_rating,
            ),
            GameSelector(
                _filter=lambda game: game.combined_rating >= 0.8,
                name="Very Positive Games",
                custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
                sort=lambda g: g.game.combined_rating,
                reverse_sort=True,
            ),
            GameSelector(
                _filter=lambda game: game.genre == ExcelGenre.VISUAL_NOVEL,
                name="Visual Novels",
            ),
            GameSelector(
                _filter=lambda _g: _g.vr,
                name="VR",
                include_in_picks=False,
            ),
            GameSelector(
                self.__zero_percent,
                grouping=GameGrouping(
                    lambda g: f'{g.group_metadata.split(":")[0]}s',
                    subgroupings=[
                        GameGrouping(lambda g: g.group_metadata.split(":")[1].strip())
                    ],
                ),
            ),
            GameSelector(
                _filter=lambda g: any(
                    x in y
                    for x, y in itertools.product(
                        ["zach", "zack", "zak", "zac", "zax"],
                        [
                            g.normal_title,
                            g.developer.lower(),
                            g.publisher.lower(),
                        ],
                    )
                ),
                name="Zach Games",
            ),
            GameSelector(
                lambda _: list(
                    filter(
                        lambda g: g.playability != Playability.PLAYABLE
                        and not g.completed
                        and g.priority >= 3
                        and self.__filter_by_mode(g),
                        self._games,
                    )
                ),
                name="Unplayable High Priority",
                include_in_picks=False,
                run_on_modes=set([PickerMode.ALL]),
            ),
            GameSelector(
                lambda _: list(
                    filter(
                        lambda g: g.playability != Playability.PLAYABLE
                        and not g.completed
                        and g.priority <= 2
                        and self.__filter_by_mode(g),
                        self._games,
                    )
                ),
                name="Unplayable Low Priority",
                include_in_picks=False,
                run_on_modes=set([PickerMode.ALL]),
            ),
            GameSelector(
                _filter=lambda g: g.translation == TranslationStatus.COMPLETE
                and not g.owned,
                name="Fan Translations",
            ),
            GameSelector(
                _filter=lambda g: any(
                    self._validator.titles_equal_normalized(g.title, mg)
                    for mg in self.__get_mobygames_titles(18173)
                ),
                skip_unless_specified=True,
                name="Survivors Likes",
            ),
            GameSelector(
                _filter=lambda g: any(
                    self._validator.titles_equal_normalized(g.title, mg)
                    for mg in self.__get_mobygames_titles(8497)
                ),
                skip_unless_specified=True,
                name="Picross",
            ),
            GameSelector(
                _filter=lambda g: any(
                    self._validator.titles_equal_normalized(g.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-9982")
                ),
                name="Soulslikes",
                skip_unless_specified=True,
            ),
            GameSelector(
                _filter=lambda g: any(
                    self._validator.titles_equal_normalized(g.title, mg)
                    for mg in self.__get_mobygames_titles(2508)
                )
                or any(
                    self._validator.titles_equal_normalized(g.title, mg)
                    for mg in self.__get_mobygames_titles(10842)
                )
                or any(
                    self._validator.titles_equal_normalized(g.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-1058")
                )
                or any(
                    self._validator.titles_equal_normalized(g.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-96")
                )
                or any(
                    self._validator.titles_equal_normalized(g.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-6118")
                )
                or any(
                    self._validator.titles_equal_normalized(g.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-4654")
                )
                or any(
                    self._validator.titles_equal_normalized(g.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-5417")
                )
                or any(
                    self._validator.titles_equal_normalized(g.title, gbg)
                    for gbg in self.__get_gb_titles_for_concept("3015-2362")
                ),
                skip_unless_specified=True,
                name="S Games",
            ),
            GameSelector(
                lambda _: list(
                    filter(
                        lambda g: self.__filter_by_mode(g)
                        and g.playing_status is not None,
                        self._games,
                    )
                ),
                grouping=GameGrouping(
                    lambda g: g.playing_status.name.replace("_", " ").title(),
                    subgroupings=[GameGrouping(should_rank=False)],
                    should_rank=False,
                ),
                name="Now Playing",
                include_in_picks=False,
                include_platform=False,
                run_on_modes=set([PickerMode.ALL]),
            ),
            GameSelector(
                self.__backloggd_top,
                grouping=GameGrouping(lambda _: "Trending"),
                sort=lambda g: g.game.group_metadata,
                custom_prefix=lambda g: f"{g.group_metadata + 1}. ",
                skip_unless_specified=True,
                no_force=True,
            ),
            GameSelector(
                custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
                sort=lambda g: g.game.combined_rating,
                reverse_sort=True,
                name="Best By Genre",
                grouping=GameGrouping(lambda g: g.genre, take=10),
            ),
            GameSelector(
                _filter=lambda g: g.estimated_playtime is not None,
                sort=lambda g: g.game.estimated_playtime,
                name="Shortest By Genre",
                grouping=GameGrouping(lambda g: g.genre, take=10),
            ),
            GameSelector(
                _filter=lambda g: g.estimated_playtime is not None,
                sort=lambda g: g.game.estimated_playtime,
                name="Shortest By Year",
                grouping=GameGrouping(lambda g: g.release_year, take=10),
            ),
            GameSelector(
                grouping=GameGrouping(
                    sort=lambda kvp: get_or_set(
                        platform_progress, kvp[0], self._played_games
                    )
                    / get_or_set(
                        total_platform,
                        kvp[0],
                        self._played_games + self._unplayed_candidates,
                    ),
                    reverse=True,
                    progress_indicator=lambda kvp: (
                        get_or_set(platform_progress, kvp[0], self._played_games),
                        get_or_set(
                            total_platform,
                            kvp[0],
                            self._played_games + self._unplayed_candidates,
                        ),
                    ),
                ),
                include_in_picks=False,
                name="Platform Progress",
            ),
            GameSelector(
                name="Percentiles",
                grouping=GameGrouping(
                    lambda g: (
                        f"0-24th (<{self._p25:.02%})"
                        if g.combined_rating < self._p25
                        else (
                            f"25-49th ({self._p25:.02%}-{self._med:.02%})"
                            if g.combined_rating < self._med
                            else (
                                f"50-74th ({self._med:.02%}-{self._p75:.02%})"
                                if g.combined_rating < self._p75
                                else (
                                    f"75-89th ({self._p75:.02%}-{self._p90:.02%})"
                                    if g.combined_rating < self._p90
                                    else (
                                        f"90-94th ({self._p90:.02%}-{self._p95:.02%})"
                                        if g.combined_rating < self._p95
                                        else (
                                            f"95-98th ({self._p95:.02%}-{self._p99:.02%})"
                                            if g.combined_rating < self._p99
                                            else f"99th (>={self._p99:.02%})"
                                        )
                                    )
                                )
                            )
                        )
                    ),
                    reverse=True,
                ),
                custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
                sort=lambda g: g.game.combined_rating,
                reverse_sort=True,
                run_on_modes=set([PickerMode.ALL]),
            ),
            GameSelector(
                _filter=lambda g: g.franchise is not None
                and (
                    any(
                        self._validator.titles_equal_normalized(g.title, mg)
                        for mg in self.__get_mobygames_titles(16538)
                    )
                    or any(
                        self._validator.titles_equal_normalized(g.title, gbg)
                        for gbg in self.__get_gb_titles_for_concept("3015-340")
                    )
                    or g.normal_title.endswith(" hd")
                    or g.normal_title.endswith(" edition")
                    or (
                        len(g.normal_title.split()) > 1
                        and (
                            g.normal_title.split()[-1].startswith("remast")
                            or g.normal_title.split()[-1].startswith("re-")
                        )
                    )
                ),
                skip_unless_specified=True,
                name="Alternate Editions",
                run_on_modes=set([PickerMode.ALL]),
            ),
            GameSelector(
                _filter=lambda g: g.notes == "Virtual Console", name="Virtual Console"
            ),
            GameSelector(
                lambda _: list(
                    filter(
                        lambda g: self.__filter_low_priority(g)
                        and self.__filter_untranslated_text_heavy(g)
                        and self.__filter_unreleased(g)
                        and self.__filter_played(g)
                        and g.platform == ExcelPlatform.PC
                        and not g.owned
                        and g.notes != "Freeware",
                        self._games,
                    )
                ),
                name="Unowned PC Games",
                include_platform=False,
                grouping=GameGrouping(
                    lambda g: g.playability.name.title(),
                    subgroupings=[GameGrouping(lambda g: g.release_year)],
                ),
                run_on_modes=set([PickerMode.ALL]),
            ),
            GameSelector(
                _filter=lambda g: g.genre == ExcelGenre.RAIL_SHOOTER,
                name="Rail Shooters",
            ),
            GameSelector(
                lambda _: (self._games_on_order),
                name="Games on Order",
                include_platform=False,
                grouping=GameGrouping(
                    lambda g: g.order_vendor,
                    subgroupings=[GameGrouping()],
                    custom_suffix=lambda kvp: f" - ${sum(g.game.purchase_price for g in kvp[1]):,.2f}",
                    should_rank=False,
                ),
                include_in_picks=False,
                run_on_modes=set([PickerMode.ALL]),
                custom_suffix=lambda g: f" (${g.purchase_price:.2f})",
            ),
            GameSelector(
                lambda _: list(
                    filter(
                        lambda g: g.date_purchased is not None
                        and g.date_completed is not None,
                        self._played_games,
                    )
                ),
                name="Purchase to Completion Gaps",
                sort=lambda g: g.game.date_completed - g.game.date_purchased,
                reverse_sort=True,
                custom_suffix=lambda g: f" - {(g.date_completed - g.date_purchased).days:,} days, {(g.date_completed - g.date_purchased).days / 365:,.1f} years (Purchase: {g.date_purchased.strftime('%m/%d/%Y')}, Completion: {g.date_completed.strftime('%m/%d/%Y')})",
                grouping=GameGrouping(
                    lambda _: "Time Between Purchase", take=100, should_rank=False
                ),
                run_on_modes=set([PickerMode.ALL]),
                include_in_picks=False,
            ),
            GameSelector(
                _filter=lambda g: g.genre
                in (
                    ExcelGenre.SIDE_SCROLLING_PLATFORMER,
                    ExcelGenre.ACTION_PLATFORMER,
                    ExcelGenre.ADVENTURE_PLATFORMER,
                    ExcelGenre.PUZZLE_PLATFORMER,
                ),
                name="2D Platformers",
            ),
            GameSelector(
                _filter=lambda g: g.franchise is not None,
                name="Most Played Franchises",
                grouping=GameGrouping(
                    lambda g: g.franchise,
                    get_group_name=lambda kvp: f"{kvp[0]} ({sum(g.game.completion_time or 0 for g in kvp[1]):,.2f}hr)",
                    sort=lambda kvp: sum(g.game.completion_time or 0 for g in kvp[1]),
                    reverse=True,
                    should_rank=False,
                    _filter=lambda kvp: sum(g.game.completion_time or 0 for g in kvp[1])
                    > 0,
                ),
                include_in_picks=False,
                run_on_modes=set([PickerMode.ALL]),
                games=self._played_games,
                custom_suffix=lambda g: (
                    f" [{g.completion_time:,.2f}hr]"
                    if g.completion_time is not None
                    else ""
                ),
                enabled=False,
            ),
            GameSelector(
                name="Most Played Genres",
                grouping=GameGrouping(
                    lambda g: g.genre,
                    get_group_name=lambda kvp: f"{kvp[0]} ({sum(g.game.completion_time or 0 for g in kvp[1]):,.2f}hr)",
                    sort=lambda kvp: sum(g.game.completion_time or 0 for g in kvp[1]),
                    reverse=True,
                    should_rank=False,
                    _filter=lambda kvp: sum(g.game.completion_time or 0 for g in kvp[1])
                    > 0,
                ),
                include_in_picks=False,
                run_on_modes=set([PickerMode.ALL]),
                games=self._played_games,
                custom_suffix=lambda g: (
                    f" [{g.completion_time:,.2f}hr]"
                    if g.completion_time is not None
                    else ""
                ),
                enabled=False,
            ),
            GameSelector(
                lambda gs: asyncio.run(self.__completed_values(gs)),
                name="Completed Values",
                run_on_modes=set([PickerMode.ALL]),
                games=list(
                    filter(
                        lambda g: g.owned_format in ("Both", "Physical"),
                        self._played_games,
                    )
                ),
                include_in_picks=False,
                grouping=GameGrouping(
                    lambda g: (
                        self.CONDIITON_MAPPING[g.owned_condition]
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
                    f" - ${g.group_metadata / 100:,.2f}"
                    if g.group_metadata is not None
                    else ""
                ),
                sort=lambda g: g.game.group_metadata or g.game.normal_title,
                reverse_sort=True,
                skip_unless_specified=True,
                no_force=True,
            ),
            GameSelector(
                name="Unplayed Wishlisted",
                run_on_modes=set([PickerMode.ALL]),
                games=list(
                    filter(lambda g: not g.completed and g.wishlisted, self._games)
                ),
                include_in_picks=False,
            ),
            GameSelector(
                self.__sheet_validations,
                games=self._games,
                run_on_modes=set([PickerMode.ALL]),
                include_in_picks=False,
                grouping=GameGrouping(lambda g: g.group_metadata, should_rank=False),
            ),
            GameSelector(
                self.__non_downloaded_games,
                run_on_modes=set([PickerMode.ALL]),
                include_in_picks=False,
                skip_unless_specified=True,
                no_force=True,
                grouping=GameGrouping(should_rank=False),
            ),
            GameSelector(
                self.__misspellings,
                run_on_modes=set([PickerMode.ALL]),
                include_in_picks=False,
                grouping=GameGrouping(should_rank=False),
            ),
            GameSelector(
                _filter=lambda g: g.priority == 1,
                run_on_modes=set([PickerMode.ALL]),
                games=self._games,
                include_in_picks=False,
                name="Will Not Play",
            ),
            GameSelector(
                _filter=lambda g: g.limited_print_company is not None,
                name="Limited Print Games",
                grouping=GameGrouping(lambda g: g.limited_print_company),
                run_on_modes=set([PickerMode.ALL]),
            ),
            GameSelector(
                _filter=lambda g: g.delisted,
                name="Delisted Games",
                run_on_modes=set([PickerMode.ALL]),
                include_in_picks=False,
            ),
            GameSelector(
                name="All Games",
                sort=lambda pg: pg.game.release_date,
                reverse_sort=True,
                custom_prefix=lambda g: (
                    datetime.datetime.strftime(g.release_date, "%b %d: ")
                    if g.fuzzy_date is None
                    else (
                        datetime.datetime.strftime(g.release_date, "%b: ")
                        if g.fuzzy_date == FuzzyDateType.MONTH_AND_YEAR_ONLY
                        else ""
                    )
                ),
                grouping=GameGrouping(
                    lambda g: g.release_year,
                    reverse=True,
                ),
            ),
            GameSelector(
                self.__incomplete_collections,
                run_on_modes=set([PickerMode.ALL]),
                include_in_picks=False,
            ),
            GameSelector(
                self.__coop_games,
                grouping=GameGrouping(
                    lambda g: (
                        "Local"
                        if g.group_metadata["local"]
                        else "Online" if g.group_metadata["online"] else "LAN"
                    ),
                ),
                custom_suffix=lambda g: f" ({', '.join(sorted(g.group_metadata['features']))})",
                include_platform=True,
            ),
        ]

        for selector in selectors:
            selector.no_cache = self._no_cache
            selector.mode = self._mode

        return sorted(
            list(filter(lambda s: s.enabled, selectors)),
            key=lambda s: s.name.casefold(),
        )

    def with_mode(self, mode: PickerMode) -> GamesPicker:
        self._mode = mode
        return self

    def run_selector(
        self,
        selector: GameSelector,
        games: List[ExcelGame],
        write_output: bool = False,
        no_diff: bool = False,
        force_picks: bool = False,
    ) -> Set[PickedGame]:
        picks: Set[PickedGame] = set([])

        selection = selector.select(games)

        full_path = picker_output.get_output_path(self._mode)

        if write_output:
            if not os.path.exists(
                f"{self.__BASE_DROPBOX_FOLDER}\\{self.__BASE_OUTPUT_PATH}"
            ):
                os.mkdir(f"{self.__BASE_DROPBOX_FOLDER}\\{self.__BASE_OUTPUT_PATH}")
            if not os.path.exists(full_path):
                os.mkdir(full_path)

        output = (
            selector.description + "\n\n"
            if selector.description is not None and write_output
            else ""
        )

        for group_name, group in selector.grouping.get_groups(
            selection, _sorted=True
        ).items():
            level = 0
            group_name = selector.grouping.get_group_name((group_name, group))

            if write_output:
                output = picker_output.get_group_output(
                    output,
                    group_name,
                    group,
                    self._name_collisions,
                    selector,
                    selector.grouping,
                    level,
                )

                subgrouping_iter = iter(selector.grouping.subgroupings)
                next_sg = next(subgrouping_iter, None)
                output = picker_output.get_subgrouping_output(
                    subgrouping_iter,
                    next_sg,
                    group,
                    level + 1,
                    selector,
                    output,
                    self._name_collisions,
                )
            if selector.include_in_picks or force_picks:
                for pick in group:
                    pick.selection_name = selector.name
                picks = picks.union(set(group))

        output = output.strip()
        file_name = f"{full_path}\\{selector.get_output_file_name()}"
        if any(output):
            was_created = False

            if not os.path.isfile(file_name):
                with open(file_name, "w", encoding="utf-8") as f:
                    print(f"Created {file_name}")
                    was_created = True

            with open(file_name, "r+", encoding="utf-8") as f:
                og_f_lines = []
                o_lines = []
                diff_lines = []

                if not was_created:
                    og_f_lines = f.read().splitlines()
                    o_lines = output.splitlines()

                    diff_lines = list(
                        unified_diff(
                            og_f_lines,
                            o_lines,
                            fromfile=file_name,
                            tofile=f"Updated {file_name}",
                            lineterm="",
                            n=0,
                        )
                    )

                if was_created or any(diff_lines):
                    f.seek(0)
                    f.write(output)
                    f.truncate()

                    if was_created or no_diff:
                        return picks

                    for line in diff_lines:
                        printed = False
                        for prefix in ("---", "+++", "@@"):
                            if line.startswith(prefix):
                                print(line)
                                printed = True
                        if printed:
                            continue

                        if line.startswith("-"):
                            print(LoggingDecorator.as_color(line, LoggingColor.RED))
                        elif line.startswith("+"):
                            print(LoggingDecorator.as_color(line, LoggingColor.GREEN))
        elif not any(output) and write_output and os.path.isfile(file_name):
            os.remove(file_name)
            print(f"Completed {file_name}!")

        return picks

    def pick_game(
        self,
        selector_names: Optional[List[str]] = None,
        write_output: bool = False,
        no_diff: bool = False,
        platform: Optional[str] = None,
        force: bool = False,
    ) -> PickedGame:
        unplayed = list(
            filter(
                lambda g: (
                    platform is None
                    or self._validator.titles_equal_normalized(
                        platform, g.platform.value
                    )
                )
                and self.__filter_by_mode(g),
                self._unplayed_candidates,
            )
        )

        picks: Set[PickedGame] = set()
        selectors = self.get_selectors()

        if selector_names and any(selector_names):
            selectors = list(
                filter(lambda s: s.name.lower().strip() in selector_names, selectors)
            )

            if not any(selectors):
                raise ValueError("One or more invalid selector name")

        valid_selectors = []

        for selector in selectors:
            should_skip = selector.skip_unless_specified

            if platform:
                selector.no_cache = True

            if force and not selector.no_force:
                should_skip = False

            if ((not selector_names or not any(selector_names)) and should_skip) or (
                not selector.include_in_picks and not write_output
            ):
                continue

            valid_selectors.append(selector)

            picks = picks.union(
                self.run_selector(selector, unplayed, write_output, no_diff)
            )

        if write_output:
            self.__cleanup()

        return random.choice(list(picks)) if any(picks) else None

    def search(self, title: str, p: int = 0) -> ExcelGame:
        matches: List[Tuple[ExcelGame, float]] = []

        def search_impl(_games: List[ExcelGame], source: str = ""):
            for game in _games:
                t1 = self._validator.normalize(title)
                t2 = self._validator.normalize(game.title)
                rat = SequenceMatcher(
                    None,
                    t1,
                    t2,
                ).ratio()

                contained = t1 in t2
                if rat >= 0.76 or contained:
                    game.title += " (Owned)" if game.owned else ""
                    if any(source):
                        game.title = f"{game.title} ({source})"
                    game.compute_properties()
                    matches.append((game, rat, contained))

        search_impl(self._games)
        search_impl(self._games_on_order, "Games on Order")

        sorted_matches = sorted(matches, key=lambda t: (t[2], t[1]), reverse=True)

        for game, _, _ in sorted_matches[10 * p : 10 * (p + 1)]:
            print(game.full_name)
        if any(sorted_matches[10 * (p + 1) :]):
            num_rem = len(sorted_matches[10 * (p + 1) :])
            print(f"{num_rem} more match{'' if num_rem == 1 else 'es'}, use -p to page")
        pages = math.ceil(len(sorted_matches) / 10)
        first_pages = " ".join(
            (
                str(i)
                if p + 1 != i
                else LoggingDecorator.as_color(str(i), LoggingColor.GREEN)
            )
            for i in range(1, min(6, pages + 1))
        )
        last_pages = ""
        highlighted_slice = " ... " if pages > 10 else " " if pages > 5 else ""
        if p + 1 > 5 and p + 1 < pages - 5:
            leading_elip = " ... " if p + 1 > 8 else " "
            trailing_elip = " ... " if p + 1 < pages - 8 else " "
            slice_port = " ".join(
                (
                    str(i)
                    if p + 1 != i
                    else LoggingDecorator.as_color(str(i), LoggingColor.GREEN)
                )
                for i in range(max(6, p - 1), min(74, p + 4))
            )
            highlighted_slice = f"{leading_elip}{slice_port}{trailing_elip}"
        if pages > 5:
            last_pages = f"{' '.join(str(i) if p + 1 != i else LoggingDecorator.as_color(str(i), LoggingColor.GREEN) for i in range(max(6, pages - 5), pages + 1))}"
        if not any(first_pages):
            first_pages = "No Results"
        print(f"<{first_pages}{highlighted_slice}{last_pages}>")

    def completion(self):
        incomplete = list(filter(self.__filter_by_mode, self._unplayed_candidates))
        complete = len(self._played_games) / (len(incomplete) + len(self._played_games))
        hr_rem = sum(g.estimated_playtime or 0 for g in incomplete)
        daily_hr = 2

        hr_so_far = sum(g.completion_time or 0 for g in self._played_games)

        print(
            f"{complete:.02%} ({len(self._played_games)}/{len(self._played_games)+len(incomplete)}) complete ({int(hr_so_far):,}hr). {int(hr_rem):,}hr (or {int(hr_rem / daily_hr):,} days, {int(hr_rem / daily_hr / 7):,} weeks, {int(hr_rem / daily_hr / 7 / 52)} years @ {daily_hr}hr/day) remaining."
        )
