from typing import Any, Dict, List, Set
import datetime
import math

from excel_game import (
    ExcelGame,
    ExcelGenre,
    Playability,
    TranslationStatus,
)

from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
import game_selectors as gs
from picked_game import PickedGame
from picker_enums import PickerMode


class SelectorLibrary:
    _data_provider: DataProvider
    _mode: PickerMode
    _library: Dict[gs.Selector, GameSelector]

    def __init__(self, data_provider: DataProvider, mode: PickerMode):
        self._data_provider = data_provider
        self._mode = mode
        self.__create_library()

    def __create_library(self):
        top_developers = gs.get_top_developers(self._data_provider.get_games())

        self._library = {
            gs.Selector._2D_PLATFORMERS: gs.get_multi_genre_selector(
                [
                    ExcelGenre.SIDE_SCROLLING_PLATFORMER,
                    ExcelGenre.ACTION_PLATFORMER,
                    ExcelGenre.ADVENTURE_PLATFORMER,
                    ExcelGenre.PUZZLE_PLATFORMER,
                ],
                gs.Selector._2D_PLATFORMERS.value,
            ),
            gs.Selector._3D_PLATFORMERS: gs.get_multi_genre_selector(
                [ExcelGenre._3D_PLATFORMER, ExcelGenre.FIRST_PERSON_PLATFORMER],
                gs.Selector._3D_PLATFORMERS.value,
            ),
            gs.Selector.AAA_GAMES: gs.AAA_GAMES,
            gs.Selector.ACTION_ADVENTURE_GAMES: gs.get_genre_selector(
                ExcelGenre.ACTION_ADVENTURE, gs.Selector.ACTION_ADVENTURE_GAMES.value
            ),
            gs.Selector.ALL_GAMES: gs.ALL_GAMES,
            gs.Selector.ALPHABETICAL: gs.ALPHABETICAL,
            gs.Selector.ALTERNATE_EDITIONS: gs.get_alternate_editions_selector(
                self._data_provider
            ),
            gs.Selector.BACKLOGGD_TOP: gs.get_backloggd_top_selector(
                self._data_provider
            ),
            gs.Selector.BEAT_EM_UPS: gs.get_genre_selector(
                ExcelGenre.BEAT_EM_UP, gs.Selector.BEAT_EM_UPS.value
            ),
            gs.Selector.BEST_BY_GENRE: gs.get_best_by_selector(
                lambda g: g.genre, gs.Selector.BEST_BY_GENRE.value
            ),
            gs.Selector.BEST_BY_PLATFORM: gs.get_best_by_selector(
                None, gs.Selector.BEST_BY_PLATFORM.value
            ),
            gs.Selector.BEST_BY_YEAR: gs.get_best_by_selector(
                lambda g: g.release_year,
                gs.Selector.BEST_BY_YEAR.value,
                reverse_grouping_sort=True,
            ),
            gs.Selector.BEST_COMPANIES_BY_METACRITIC: gs.BEST_COMPANIES_BY_METACRITIC,
            gs.Selector.BEST_YEARS_BY_METACRITIC: gs.BEST_YEARS_BY_METACRITIC,
            gs.Selector.BETWEEN_1_AND_5_HOURS: gs.get_playtime_selector(
                gs.Selector.BETWEEN_1_AND_5_HOURS.value, gs.PlaytimeBounds(1, 5)
            ),
            gs.Selector.BETWEEN_5_AND_10_HOURS: gs.get_playtime_selector(
                gs.Selector.BETWEEN_5_AND_10_HOURS.value, gs.PlaytimeBounds(5, 10)
            ),
            gs.Selector.BETWEEN_10_AND_20_HOURS: gs.get_playtime_selector(
                gs.Selector.BETWEEN_10_AND_20_HOURS.value, gs.PlaytimeBounds(10, 20)
            ),
            gs.Selector.BETWEEN_20_AND_30_HOURS: gs.get_playtime_selector(
                gs.Selector.BETWEEN_20_AND_30_HOURS.value, gs.PlaytimeBounds(20, 30)
            ),
            gs.Selector.BIG_GAMES: gs.BIG_GAMES,
            gs.Selector.BIRTHDAY_GAMES: gs.BIRTHDAY_GAMES,
            gs.Selector.BOOMER_SHOOTERS: gs.get_multi_genre_selector(
                [
                    ExcelGenre.FIRST_PERSON_ACTION,
                    ExcelGenre.FIRST_PERSON_SHOOTER,
                    ExcelGenre.TACTICAL_SHOOTER,
                    ExcelGenre.THIRD_PERSON_ACTION,
                    ExcelGenre.THIRD_PERSON_SHOOTER,
                ],
                gs.Selector.BOOMER_SHOOTERS.value,
            ),
            gs.Selector.COLLECTIONS: gs.get_multi_genre_selector(
                [ExcelGenre.COMPILATION, ExcelGenre.MINIGAME_COLLECTION],
                gs.Selector.COLLECTIONS.value,
            ),
            gs.Selector.COMPLETED_GAMES_ORDERING: gs.get_completed_ordering_selector(
                self._data_provider
            ),
            gs.Selector.COMPLETED_VALUES: gs.get_completed_values_selector(
                self._data_provider
            ),
            gs.Selector.COOP_GAMES: gs.COOP_GAMES,
            gs.Selector.CYBERPUNK: gs.get_third_party_selector(
                self._data_provider,
                gs.Selector.CYBERPUNK.value,
                giant_bomb_concept_guids=["3015-6735"],
            ),
            gs.Selector.DAD_GAMES: gs.DAD_GAMES,
            gs.Selector.DELISTED_GAMES: gs.DELISTED_GAMES,
            gs.Selector.DLCS: gs.DLCS,
            gs.Selector.FAN_TRANSLATIONS: gs.FAN_TRANSLATIONS,
            gs.Selector.FAVORITES: gs.get_favorites_selector(self._data_provider),
            gs.Selector.FIGHTING_GAMES: gs.get_genre_selector(
                ExcelGenre.FIGHTING, gs.Selector.FIGHTING_GAMES.value
            ),
            gs.Selector.FIRST_PARTY_GAMES: gs.FIRST_PARTY_GAMES,
            gs.Selector.FRANCHISE_PLAYTHROUGH_CONTENDERS: gs.get_franchise_playthroughs_selector(
                self._data_provider,
                self._mode,
                gs.FRANCHISE_CONTENDERS,
                gs.Selector.FRANCHISE_PLAYTHROUGH_CONTENDERS.value,
            ),
            gs.Selector.FRANCHISE_PLAYTHROUGHS: gs.get_franchise_playthroughs_selector(
                self._data_provider, self._mode
            ),
            gs.Selector.FREEWARE: gs.FREEWARE,
            gs.Selector.FROMSOFTWARE: gs.FROMSOFTWARE,
            gs.Selector.GAMES_ON_ORDER: gs.get_games_on_order_selector(
                self._data_provider
            ),
            gs.Selector.GREATER_THAN_30_HOURS: gs.get_playtime_selector(
                gs.Selector.GREATER_THAN_30_HOURS.value, gs.PlaytimeBounds(30, None)
            ),
            gs.Selector.HACK_AND_SLASH: gs.get_genre_selector(
                ExcelGenre.HACK_AND_SLASH, gs.Selector.HACK_AND_SLASH.value
            ),
            gs.Selector.HIGHEST_PRIORITY_PLATFORMS: gs.HIGHEST_PRIORITY_PLATFORMS,
            gs.Selector.HIGH_CRITIC_RATINGS: gs.HIGH_CRITIC_RATINGS,
            gs.Selector.HIGH_PRIORITY_RATINGS: gs.HIGH_PRIORITY_RATINGS,
            gs.Selector.HIGH_USER_RATINGS: gs.HIGH_USER_RATINGS,
            gs.Selector.HORROR_GAMES: gs.get_horror_games_selector(
                self._data_provider,
            ),
            gs.Selector.IMMERSIVE_SIMS: gs.get_third_party_selector(
                self._data_provider,
                gs.Selector.IMMERSIVE_SIMS.value,
                giant_bomb_concept_guids=["3015-5700"],
            ),
            gs.Selector.INCOMPLETE_COLLECTIONS: gs.get_incomplete_collections_selector(
                self._data_provider
            ),
            gs.Selector.JRPG: gs.get_multi_genre_selector(
                [
                    ExcelGenre.ACTION_RPG,
                    ExcelGenre.COMPUTER_RPG,
                    ExcelGenre.TURN_BASED_RPG,
                    ExcelGenre.STRATEGY_RPG,
                    ExcelGenre.DUNGEON_CRAWLER,
                    ExcelGenre.MMORPG,
                ],
                gs.Selector.JRPG.value,
            ),
            gs.Selector.LARGEST_RATING_DIFFERENCES: gs.get_largest_rating_differences_selector(
                self._data_provider
            ),
            gs.Selector.LIMITED_PRINT_GAMES: gs.LIMITED_PRINT_GAMES,
            gs.Selector.LONGEST_GAMES: gs.LONGEST_GAMES,
            gs.Selector.LONGEST_PLAYTHROUGHS: gs.get_longest_playthroughs_selector(
                self._data_provider
            ),
            gs.Selector.LONGEST_TITLES: gs.LONGEST_TITLES,
            gs.Selector.MAJOR_INDIE_GAMES: gs.get_major_indie_games_selector(
                self._data_provider
            ),
            gs.Selector.MAX_PRIORITY: gs.MAX_PRIORITY,
            gs.Selector.METROIDVANIA: gs.get_genre_selector(
                ExcelGenre.METROIDVANIA, gs.Selector.METROIDVANIA.value
            ),
            gs.Selector.MISSING_PLAYTIME: gs.get_missing_playtime_selector(
                self._data_provider
            ),
            gs.Selector.MISSPELLINGS: gs.MISSPELLINGS,
            gs.Selector.MOST_CONCURRENT_PLAYTHROUGHS: gs.get_most_concurrent_playthroughs_selector(
                self._data_provider
            ),
            gs.Selector.MOST_PLAYED_DEVELOPERS: gs.get_most_played_selector(
                self._data_provider,
                lambda g: g.developer,
                gs.Selector.MOST_PLAYED_DEVELOPERS.value,
            ),
            gs.Selector.MOST_PLAYED_FRANCHISES: gs.get_most_played_selector(
                self._data_provider,
                lambda g: g.franchise,
                gs.Selector.MOST_PLAYED_FRANCHISES.value,
                _filter=lambda g: g.franchise is not None,
            ),
            gs.Selector.MOST_PLAYED_GENRES: gs.get_most_played_selector(
                self._data_provider,
                lambda g: g.genre,
                gs.Selector.MOST_PLAYED_GENRES.value,
            ),
            gs.Selector.MOST_PLAYED_PLATFORMS: gs.get_most_played_selector(
                self._data_provider,
                lambda g: g.platform,
                gs.Selector.MOST_PLAYED_PLATFORMS.value,
            ),
            gs.Selector.MOST_PLAYED_YEARS: gs.get_most_played_selector(
                self._data_provider,
                lambda g: g.release_year,
                gs.Selector.MOST_PLAYED_YEARS.value,
            ),
            gs.Selector.NO_ESTIMATED_PLAYTIME: gs.NO_ESTIMATED_PLAYTIME,
            gs.Selector.NON_DOWNLOADED_GAMES: gs.get_non_downloaded_games_selector(
                self._data_provider
            ),
            gs.Selector.NON_STEAM: gs.NON_STEAM,
            gs.Selector.NOW_PLAYING: gs.get_now_playing_selector(
                self._data_provider, self._mode
            ),
            gs.Selector.OBSCURE_GAMES: gs.OBSCURE_GAMES,
            gs.Selector.OFFBEAT_GENRE_GAMES: gs.get_multi_genre_selector(
                [
                    ExcelGenre.ACTION,
                    ExcelGenre.ARCADE,
                    ExcelGenre.BOARD_GAME,
                    ExcelGenre.CARD_GAME,
                    ExcelGenre.EDUCATIONAL,
                    ExcelGenre.EXPERIMENTAL,
                    ExcelGenre.FMV,
                    ExcelGenre.GAME_CREATION,
                    ExcelGenre.HIDDEN_OBJECT,
                    ExcelGenre.PINBALL,
                    ExcelGenre.RHYTHM,
                    ExcelGenre.RUNNER,
                    ExcelGenre.SPORTS,
                    ExcelGenre.STEALTH_ACTION,
                    ExcelGenre.SURVIVAL,
                    ExcelGenre.TOWER_DEFENSE,
                    ExcelGenre.TRIVIA,
                ],
                gs.Selector.OFFBEAT_GENRE_GAMES.value,
            ),
            gs.Selector.ONE_PER_ADDED_DATE_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Added Date",
                self._data_provider,
                lambda g: (
                    g.date_added.strftime("%B, %Y")
                    if g.date_added is not None
                    else "No Added Date"
                ),
                games_override=list(
                    filter(
                        lambda g: g.date_added is not None,
                        self._data_provider.get_unplayed_candidates(),
                    )
                ),
                custom_grouping_sort=lambda kvp: kvp[1][-1].game.date_added
                or datetime.datetime.max,
                custom_grouping_sort_reverse=True,
            ),
            gs.Selector.ONE_PER_ADDED_DATE_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Added Date",
                self._data_provider,
                lambda g: (
                    g.date_added.strftime("%B, %Y")
                    if g.date_added is not None
                    else "No Added Date"
                ),
                games_override=list(
                    filter(
                        lambda g: g.date_added is not None,
                        self._data_provider.get_played_games(),
                    )
                ),
                custom_grouping_sort=lambda kvp: kvp[1][-1].game.date_added
                or datetime.datetime.max,
                custom_grouping_sort_reverse=True,
                completions=True,
            ),
            gs.Selector.ONE_PER_ALPHABET_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Letter", self._data_provider, gs.get_alphabetical_first_letter
            ),
            gs.Selector.ONE_PER_ALPHABET_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Letter",
                self._data_provider,
                gs.get_alphabetical_first_letter,
                games_override=self._data_provider.get_played_games(),
                completions=True,
            ),
            gs.Selector.ONE_PER_FAN_TRANSLATION_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Fan Translation",
                self._data_provider,
                lambda g: gs.get_platform_completion_id(g)
                + f" ({'Translated' if g.translation == TranslationStatus.COMPLETE else 'Untranslated'})",
                games_override=list(
                    filter(
                        lambda g: g.translation == TranslationStatus.COMPLETE
                        and not g.owned,
                        self._data_provider.get_unplayed_candidates(),
                    )
                ),
            ),
            gs.Selector.ONE_PER_FAN_TRANSLATION_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Fan Translation",
                self._data_provider,
                lambda g: gs.get_platform_completion_id(g)
                + f" ({'Translated' if g.translation == TranslationStatus.COMPLETE else 'Untranslated'})",
                games_override=list(
                    filter(
                        lambda g: g.translation == TranslationStatus.COMPLETE
                        and not g.owned,
                        self._data_provider.get_played_games(),
                    )
                ),
                completions=True,
            ),
            gs.Selector.ONE_PER_FRANCHISE_CONTENDER_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Franchise Contender",
                self._data_provider,
                lambda g: g.franchise,
                games_override=list(
                    filter(
                        lambda g: g.franchise in gs.FRANCHISE_CONTENDERS,
                        self._data_provider.get_unplayed_candidates(),
                    )
                ),
            ),
            gs.Selector.ONE_PER_FRANCHISE_CONTENDER_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Franchise Contender",
                self._data_provider,
                lambda g: g.franchise,
                games_override=list(
                    filter(
                        lambda g: g.franchise in gs.FRANCHISE_CONTENDERS,
                        self._data_provider.get_played_games(),
                    )
                ),
                completions=True,
            ),
            gs.Selector.ONE_PER_GENRE_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Genre", self._data_provider, lambda g: g.genre
            ),
            gs.Selector.ONE_PER_GENRE_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Genre",
                self._data_provider,
                lambda g: g.genre,
                games_override=self._data_provider.get_played_games(),
                completions=True,
            ),
            gs.Selector.ONE_PER_LIMITED_PRINT_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Limited Print",
                self._data_provider,
                lambda g: g.limited_print_company,
                games_override=list(
                    filter(
                        lambda g: g.limited_print_company is not None,
                        self._data_provider.get_unplayed_candidates(),
                    )
                ),
            ),
            gs.Selector.ONE_PER_LIMITED_PRINT_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Limited Print",
                self._data_provider,
                lambda g: g.limited_print_company,
                games_override=list(
                    filter(
                        lambda g: g.limited_print_company is not None,
                        self._data_provider.get_played_games(),
                    )
                ),
                completions=True,
            ),
            # Completed 2 times
            gs.Selector.ONE_PER_PERCENTILE_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Percentile",
                self._data_provider,
                lambda g: gs.group_by_percentile(g, self._data_provider),
                challenge_start=datetime.datetime(2025, 2, 5),
                custom_grouping_sort=lambda kvp: self._data_provider.get_percentile_ranking_for_game(
                    kvp[1][-1].game
                ).value,
                custom_grouping_sort_reverse=True,
            ),
            gs.Selector.ONE_PER_PERCENTILE_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Percentile",
                self._data_provider,
                lambda g: gs.group_by_percentile(g, self._data_provider),
                games_override=self._data_provider.get_played_games(),
                completions=True,
                challenge_start=datetime.datetime(2025, 2, 5),
                custom_grouping_sort=lambda kvp: self._data_provider.get_percentile_ranking_for_game(
                    kvp[1][-1].game
                ).value,
                custom_grouping_sort_reverse=True,
            ),
            gs.Selector.ONE_PER_PLATFORM_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Platform",
                self._data_provider,
                gs.get_platform_completion_id,
            ),
            gs.Selector.ONE_PER_PLATFORM_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Platform",
                self._data_provider,
                gs.get_platform_completion_id,
                games_override=self._data_provider.get_played_games(),
                completions=True,
            ),
            gs.Selector.ONE_PER_PLATFORM_CHALLENGE_UNPLAYABLE: gs.get_one_per_criteria_challenge_selector(
                "Platform",
                self._data_provider,
                gs.get_platform_completion_id,
                games_override=list(
                    filter(
                        lambda g: g.playability != Playability.PLAYABLE
                        and not g.completed,
                        self._data_provider.get_games(),
                    )
                ),
                challenge_suffix="Unplayable",
            ),
            gs.Selector.ONE_PER_PLAYTIME_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Playtime",
                self._data_provider,
                gs.get_playtime,
                custom_grouping_sort=lambda kvp: (
                    kvp[1][-1].game.estimated_playtime or 0
                )
                // 1,
            ),
            gs.Selector.ONE_PER_PLAYTIME_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Playtime",
                self._data_provider,
                gs.get_playtime,
                games_override=self._data_provider.get_played_games(),
                completions=True,
                custom_grouping_sort=lambda kvp: (kvp[1][-1].game.completion_time or 0)
                // 1,
            ),
            gs.Selector.ONE_PER_PURCHASE_DATE_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Purchase Date",
                self._data_provider,
                lambda g: (
                    g.date_purchased.strftime("%B, %Y")
                    if g.date_purchased is not None
                    else "Not Purchased"
                ),
                games_override=list(
                    filter(
                        lambda g: g.date_purchased is not None,
                        self._data_provider.get_unplayed_candidates(),
                    )
                ),
                custom_grouping_sort=lambda kvp: kvp[1][-1].game.date_purchased
                or datetime.datetime.max,
                custom_grouping_sort_reverse=True,
            ),
            gs.Selector.ONE_PER_PURCHASE_DATE_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Purchase Date",
                self._data_provider,
                lambda g: (
                    g.date_purchased.strftime("%B, %Y")
                    if g.date_purchased is not None
                    else "Not Purchased"
                ),
                games_override=list(
                    filter(
                        lambda g: g.date_purchased is not None,
                        self._data_provider.get_played_games(),
                    )
                ),
                custom_grouping_sort=lambda kvp: kvp[1][-1].game.date_purchased
                or datetime.datetime.max,
                custom_grouping_sort_reverse=True,
                completions=True,
            ),
            gs.Selector.ONE_PER_PURCHASE_PRICE_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Purchase Price",
                self._data_provider,
                lambda g: (
                    f"${int(g.purchase_price)}.00"
                    if int(g.purchase_price or 0) > 0
                    else "Free"
                ),
                games_override=list(
                    filter(
                        lambda g: g.purchase_price is not None and g.purchase_price > 0,
                        self._data_provider.get_unplayed_candidates(),
                    )
                ),
                custom_grouping_sort=lambda kvp: int(kvp[1][0].game.purchase_price),
            ),
            gs.Selector.ONE_PER_PURCHASE_PRICE_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Purchase Price",
                self._data_provider,
                lambda g: (
                    f"${int(g.purchase_price)}.00"
                    if int(g.purchase_price or 0) > 0
                    else "Free"
                ),
                games_override=list(
                    filter(
                        lambda g: g.purchase_price is not None
                        and int(g.purchase_price) > 0,
                        self._data_provider.get_played_games(),
                    )
                ),
                custom_grouping_sort=lambda kvp: int(kvp[1][0].game.purchase_price),
                completions=True,
            ),
            # Completed 1 time
            gs.Selector.ONE_PER_RATING_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Rating",
                self._data_provider,
                lambda g: f"{math.floor(g.combined_rating * 10) * 10}%",
                challenge_start=datetime.datetime(2025, 2, 8),
            ),
            gs.Selector.ONE_PER_RATING_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Rating",
                self._data_provider,
                lambda g: f"{math.floor(g.combined_rating * 10) * 10}%",
                games_override=self._data_provider.get_played_games(),
                completions=True,
                challenge_start=datetime.datetime(2025, 2, 8),
            ),
            gs.Selector.ONE_PER_REGION_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Region",
                self._data_provider,
                lambda g: g.release_region.name.replace("_", " ").title(),
            ),
            gs.Selector.ONE_PER_REGION_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Region",
                self._data_provider,
                lambda g: g.release_region.name.replace("_", " ").title(),
                games_override=self._data_provider.get_played_games(),
                completions=True,
            ),
            gs.Selector.ONE_PER_TITLE_LENGTH_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Title Length",
                self._data_provider,
                lambda g: len(g.title.replace(" ", "")),
                custom_grouping_sort=lambda kvp: int(kvp[0]),
            ),
            gs.Selector.ONE_PER_TITLE_LENGTH_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Title Length",
                self._data_provider,
                lambda g: len(g.title.replace(" ", "")),
                games_override=self._data_provider.get_played_games(),
                completions=True,
                custom_grouping_sort=lambda kvp: int(kvp[0]),
            ),
            gs.Selector.ONE_PER_TOP_DEVELOPER_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Top Developer",
                self._data_provider,
                lambda g: g.developer,
                games_override=list(
                    filter(
                        lambda g: g.developer in top_developers,
                        self._data_provider.get_unplayed_candidates(),
                    )
                ),
            ),
            gs.Selector.ONE_PER_TOP_DEVELOPER_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Top Developer",
                self._data_provider,
                lambda g: g.developer,
                games_override=list(
                    filter(
                        lambda g: g.developer in top_developers,
                        self._data_provider.get_played_games(),
                    )
                ),
                completions=True,
            ),
            gs.Selector.ONE_PER_YEAR_CHALLENGE: gs.get_one_per_criteria_challenge_selector(
                "Year", self._data_provider, lambda g: g.release_year
            ),
            gs.Selector.ONE_PER_YEAR_CHALLENGE_COMPLETIONS: gs.get_one_per_criteria_challenge_selector(
                "Year",
                self._data_provider,
                lambda g: g.release_year,
                games_override=self._data_provider.get_played_games(),
                completions=True,
            ),
            gs.Selector.PALINDROMES: gs.PALINDROME_GAMES,
            gs.Selector.PERCENTILES: gs.get_percentiles_selector(self._data_provider),
            gs.Selector.PHYSICAL_GAMES: gs.PHYSICAL_GAMES,
            gs.Selector.PICROSS: gs.get_third_party_selector(
                self._data_provider,
                gs.Selector.PICROSS.value,
                moby_games_group_ids=[8497],
            ),
            gs.Selector.PLATFORM_PROGRESS: gs.get_platform_progress_selector(
                self._data_provider
            ),
            gs.Selector.PLAYED_PURCHASES: gs.get_played_purchases_selector(
                self._data_provider
            ),
            gs.Selector.POINT_AND_CLICK_GAMES: gs.get_multi_genre_selector(
                [ExcelGenre.ADVENTURE, ExcelGenre.TEXT_ADVENTURE],
                gs.Selector.POINT_AND_CLICK_GAMES.value,
            ),
            gs.Selector.POTENTIAL_DUPLICATES: gs.POTENTIAL_DUPLICATES,
            gs.Selector.PURCHASE_TO_COMPLETION_GAPS: gs.get_purchase_to_completion_gaps_selector(
                self._data_provider
            ),
            gs.Selector.PUZZLE_GAMES: gs.get_multi_genre_selector(
                [
                    ExcelGenre.PUZZLE,
                    ExcelGenre.PUZZLE_ACTION,
                    ExcelGenre.FIRST_PERSON_PUZZLE,
                ],
                name=gs.Selector.PUZZLE_GAMES.value,
            ),
            gs.Selector.QUARTERLY_SPEND: gs.get_quarterly_spend_selector(
                self._data_provider
            ),
            gs.Selector.RAIL_SHOOTERS: gs.get_genre_selector(
                ExcelGenre.RAIL_SHOOTER, gs.Selector.RAIL_SHOOTERS.value
            ),
            gs.Selector.RUN_AND_GUN: gs.get_genre_selector(
                ExcelGenre.RUN_AND_GUN, gs.Selector.RUN_AND_GUN.value
            ),
            gs.Selector.S_GAMES: gs.get_third_party_selector(
                self._data_provider,
                gs.Selector.S_GAMES.value,
                giant_bomb_concept_guids=[
                    "3015-1058",
                    "3015-96",
                    "3015-6118",
                    "3015-4654",
                    "3015-5417",
                    "3015-2362",
                    "3015-4955",
                ],
                moby_games_group_ids=[2508, 10842],
            ),
            gs.Selector.SAN_FRANCISCO_GAMES: gs.get_third_party_selector(
                self._data_provider,
                gs.Selector.SAN_FRANCISCO_GAMES.value,
                moby_games_group_ids=[10594],
            ),
            gs.Selector.SHEET_VALIDATIONS: gs.get_sheet_validations_selector(
                self._data_provider
            ),
            gs.Selector.SHMUPS: gs.get_multi_genre_selector(
                [
                    ExcelGenre.SCROLLING_SHOOTER,
                    ExcelGenre.SHOOTER,
                    ExcelGenre.TWIN_STICK_SHOOTER,
                ],
                gs.Selector.SHMUPS.value,
            ),
            gs.Selector.SHORTEST_BY_GENRE: gs.get_shortest_by_selector(
                lambda g: g.genre, gs.Selector.SHORTEST_BY_GENRE.value
            ),
            gs.Selector.SHORTEST_BY_YEAR: gs.get_shortest_by_selector(
                lambda g: g.release_year, gs.Selector.SHORTEST_BY_YEAR.value
            ),
            gs.Selector.SHORTEST_GAMES: gs.SHORTEST_GAMES,
            gs.Selector.SHORTEST_OVERALL: gs.SHORTEST_OVERALL,
            gs.Selector.SHORTEST_OVERALL_UNCOMMON_GENRE: gs.SHORTEST_OVERALL_UNCOMMON_GENRE,
            gs.Selector.SOULSLIKES: gs.get_third_party_selector(
                self._data_provider,
                gs.Selector.SOULSLIKES.value,
                giant_bomb_concept_guids=["3015-9982"],
            ),
            gs.Selector.STRATEGY_GAMES: gs.get_multi_genre_selector(
                [
                    ExcelGenre._4X,
                    ExcelGenre.GRAND_STRATEGY,
                    ExcelGenre.REAL_TIME_STRATEGY,
                    ExcelGenre.REAL_TIME_TACTICS,
                    ExcelGenre.SIMULATION,
                    ExcelGenre.STRATEGY,
                    ExcelGenre.TURN_BASED_STRATEGY,
                    ExcelGenre.TURN_BASED_TACTICS,
                ],
                gs.Selector.STRATEGY_GAMES.value,
            ),
            gs.Selector.SUBSCRIPTIONS: gs.SUBSCRIPTIONS,
            gs.Selector.SURVIVORS_LIKES: gs.get_third_party_selector(
                self._data_provider,
                gs.Selector.SURVIVORS_LIKES.value,
                moby_games_group_ids=[18173],
            ),
            gs.Selector.TOP_GAMES: gs.TOP_GAMES,
            gs.Selector.TOP_TEN_JRPGS: GameSelector(
                _filter=lambda g: g.genre
                in set(
                    [
                        ExcelGenre.ACTION_RPG,
                        ExcelGenre.TURN_BASED_RPG,
                        ExcelGenre.STRATEGY_RPG,
                        ExcelGenre.DUNGEON_CRAWLER,
                    ]
                ),
                name="Top 10 JRPGs",
                grouping=GameGrouping(group_size=10),
                sort=lambda pg: (pg.game.combined_rating, pg.game.normal_title),
                reverse_sort=True,
                include_platform=False,
            ),
            gs.Selector.UNDER_1_HOUR: gs.get_playtime_selector(
                gs.Selector.UNDER_1_HOUR.value, gs.PlaytimeBounds(None, 1)
            ),
            gs.Selector.UNDER_1_HOUR_UNCOMMON_GENRE: gs.UNDER_1_HOUR_UNCOMMON_GENRE,
            gs.Selector.UNDERPRIORITIZED: gs.UNDERPRIORITIZED,
            gs.Selector.UNKNOWN_PLAYABILITY: gs.get_unknown_playability_selector(
                self._data_provider, self._mode
            ),
            gs.Selector.UNORDERED_AMAZON_GAMES: gs.get_unordered_amazon_games_selector(
                self._data_provider
            ),
            gs.Selector.UNOWNED_PC_GAMES: gs.get_unowned_pc_games_selector(
                self._data_provider
            ),
            gs.Selector.UNPLAYABLE_HIGH_PRIORITY: gs.get_unplayable_high_priority_selector(
                self._data_provider, self._mode
            ),
            gs.Selector.UNPLAYABLE_LOW_PRIORITY: gs.get_unplayable_low_priority_selector(
                self._data_provider, self._mode
            ),
            gs.Selector.UNPLAYED_PURCHASES: gs.UNPLAYED_PURCHASES,
            gs.Selector.UNPLAYED_WISHLISTED: gs.get_unplayed_wishlisted_selector(
                self._data_provider
            ),
            gs.Selector.UNTRANSLATED_GAMES: gs.get_untranslated_games_selector(
                self._data_provider
            ),
            gs.Selector.VEHICLE_BASED_GAMES: gs.get_multi_genre_selector(
                [
                    ExcelGenre.FLIGHT_SIMULATION,
                    ExcelGenre.RACING,
                    ExcelGenre.SPACE_COMBAT,
                    ExcelGenre.VEHICULAR_COMBAT,
                ],
                gs.Selector.VEHICLE_BASED_GAMES.value,
            ),
            gs.Selector.VERY_BAD_GAMES: gs.VERY_BAD_GAMES,
            gs.Selector.VERY_POSITIVE_GAMES: gs.VERY_POSITIVE_GAMES,
            gs.Selector.VIRTUAL_CONSOLE: gs.VIRTUAL_CONSOLE,
            gs.Selector.VISUAL_NOVELS: gs.VISUAL_NOVELS,
            gs.Selector.VR: gs.VR,
            gs.Selector.WILL_NOT_PLAY: gs.get_will_not_play_selector(
                self._data_provider
            ),
            gs.Selector.ZACH_GAMES: gs.ZACH_GAMES,
            gs.Selector.ZERO_PERCENT: gs.get_zero_percent_selector(self._data_provider),
        }

        self._library[gs.Selector.TOP_BY_SELECTOR] = self.__get_top_by_selector()
        self._library[gs.Selector.SELECTORS_BY_GENRE] = (
            self.__get_selectors_by_condition(
                gs.Selector.SELECTORS_BY_GENRE.value,
                GameGrouping(lambda g: g.genre),
                include_platform=True,
            )
        )
        self._library[gs.Selector.SELECTORS_BY_PLATFORM] = (
            self.__get_selectors_by_condition(gs.Selector.SELECTORS_BY_PLATFORM.value)
        )

    def __get_top_by_selector(self) -> GameSelector:
        except_selectors: Set[gs.Selector] = set(
            [
                gs.Selector.COMPLETED_VALUES,
                gs.Selector.GAMES_ON_ORDER,
                gs.Selector.LARGEST_RATING_DIFFERENCES,
                gs.Selector.MISSPELLINGS,
                gs.Selector.MOST_PLAYED_FRANCHISES,
                gs.Selector.MOST_PLAYED_GENRES,
                gs.Selector.NOW_PLAYING,
                gs.Selector.ONE_PER_ALPHABET_CHALLENGE,
                gs.Selector.ONE_PER_ALPHABET_CHALLENGE_COMPLETIONS,
                gs.Selector.ONE_PER_FAN_TRANSLATION_CHALLENGE,
                gs.Selector.ONE_PER_FAN_TRANSLATION_CHALLENGE_COMPLETIONS,
                gs.Selector.ONE_PER_FRANCHISE_CONTENDER_CHALLENGE,
                gs.Selector.ONE_PER_FRANCHISE_CONTENDER_CHALLENGE_COMPLETIONS,
                gs.Selector.ONE_PER_GENRE_CHALLENGE,
                gs.Selector.ONE_PER_GENRE_CHALLENGE_COMPLETIONS,
                gs.Selector.ONE_PER_PERCENTILE_CHALLENGE,
                gs.Selector.ONE_PER_PERCENTILE_CHALLENGE_COMPLETIONS,
                gs.Selector.ONE_PER_PLATFORM_CHALLENGE,
                gs.Selector.ONE_PER_PLATFORM_CHALLENGE_COMPLETIONS,
                gs.Selector.ONE_PER_PLATFORM_CHALLENGE_UNPLAYABLE,
                gs.Selector.ONE_PER_PLAYTIME_CHALLENGE,
                gs.Selector.ONE_PER_PLAYTIME_CHALLENGE_COMPLETIONS,
                gs.Selector.ONE_PER_RATING_CHALLENGE,
                gs.Selector.ONE_PER_RATING_CHALLENGE_COMPLETIONS,
                gs.Selector.ONE_PER_REGION_CHALLENGE,
                gs.Selector.ONE_PER_REGION_CHALLENGE_COMPLETIONS,
                gs.Selector.ONE_PER_YEAR_CHALLENGE,
                gs.Selector.ONE_PER_YEAR_CHALLENGE_COMPLETIONS,
                gs.Selector.PLAYED_PURCHASES,
                gs.Selector.POTENTIAL_DUPLICATES,
                gs.Selector.PURCHASE_TO_COMPLETION_GAPS,
                gs.Selector.QUARTERLY_SPEND,
            ]
        )

        def get_selections(games: List[ExcelGame]) -> List[ExcelGame]:
            returned_games: List[ExcelGame] = []
            for selector_type, selector in self._library.items():
                if selector.skip_unless_specified or selector_type in except_selectors:
                    continue
                selection = selector.select(games)
                returned_games.extend(
                    _g.get_copy_with_metadata(selector_type.value)
                    for _g in sorted(
                        selection, key=lambda g: (g.combined_rating or 0), reverse=True
                    )[:5]
                )

            return returned_games

        return GameSelector(
            get_selections,
            name=gs.Selector.TOP_BY_SELECTOR.value,
            grouping=GameGrouping(lambda g: g.group_metadata),
            sort=lambda pg: (pg.game.combined_rating or 0),
            reverse_sort=True,
            skip_unless_specified=True,
            run_on_modes=set([PickerMode.ALL]),
        )

    def __get_selectors_by_condition(
        self,
        name: str,
        _grouping: GameGrouping = GameGrouping(),
        include_platform: bool = False,
    ) -> List[GameSelector]:
        def get_new_game_when_possible(
            pg: PickedGame,
            group_key: Any,
            group: List[PickedGame],
            picked_games: List[PickedGame],
        ) -> PickedGame:
            picked_grouped = _grouping.get_groups(picked_games)
            picked_set = set(pg.game for pg in picked_grouped.get(group_key) or [])
            group.remove(pg)
            best_pick = pg

            while pg.game in picked_set and any(group):
                pg = max(
                    group,
                    key=lambda g: (g.game.combined_rating or 0, g.game.normal_title),
                )
                group.remove(pg)
                if pg.game.combined_rating > best_pick.game.combined_rating or (
                    pg.game.combined_rating == best_pick.game.combined_rating
                    and pg.game.normal_title < best_pick.game.normal_title
                ):
                    best_pick = pg

            return pg if pg.game not in picked_set else best_pick

        def get_selections(games: List[ExcelGame]) -> List[ExcelGame]:
            returned_games: List[ExcelGame] = []
            for selector_type, selector in self._library.items():
                if (
                    selector.skip_unless_specified
                    or set([PickerMode.ALL]) == selector.run_on_modes
                ):
                    continue
                selection = selector.select_groups(games).flatten()
                grouped = _grouping.get_groups(selection)

                for key, grouped_games in grouped.items():
                    pg = get_new_game_when_possible(
                        max(grouped_games, key=lambda g: g.highest_priority),
                        key,
                        grouped_games,
                        returned_games,
                    )
                    returned_games.append(
                        pg.game.get_copy_with_metadata(selector_type.value)
                    )

            return returned_games

        return GameSelector(
            get_selections,
            name=name,
            sort=lambda pg: pg.game.group_metadata,
            custom_prefix=lambda g: f"{g.group_metadata}: ",
            run_on_modes=set([PickerMode.ALL]),
            grouping=_grouping,
            include_platform=include_platform,
        )

    def update_mode(self, mode: PickerMode):
        self._mode = mode
        self._library[gs.Selector.FRANCHISE_PLAYTHROUGHS] = (
            gs.get_franchise_playthroughs_selector(self._data_provider, self._mode)
        )
        self._library[gs.Selector.FRANCHISE_PLAYTHROUGH_CONTENDERS] = (
            gs.get_franchise_playthroughs_selector(
                self._data_provider,
                self._mode,
                gs.FRANCHISE_CONTENDERS,
                gs.Selector.FRANCHISE_PLAYTHROUGH_CONTENDERS.value,
            )
        )
        self._library[gs.Selector.UNPLAYABLE_HIGH_PRIORITY] = (
            gs.get_unplayable_high_priority_selector(self._data_provider, self._mode)
        )
        self._library[gs.Selector.UNPLAYABLE_LOW_PRIORITY] = (
            gs.get_unplayable_low_priority_selector(self._data_provider, self._mode)
        )
        self._library[gs.Selector.NOW_PLAYING] = gs.get_now_playing_selector(
            self._data_provider, self._mode
        )
        self._library[gs.Selector.UNKNOWN_PLAYABILITY] = (
            gs.get_unknown_playability_selector(self._data_provider, self._mode)
        )

    def get(self, selector: gs.Selector) -> GameSelector:
        return self._library[selector]

    def all(self) -> List[GameSelector]:
        return list(self._library.values())
