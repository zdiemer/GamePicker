from .selector_enums import Selector

# Characteristics
from .characteristics.alphabetical import ALPHABETICAL
from .characteristics.coop_games import COOP_GAMES
from .characteristics.delisted_games import DELISTED_GAMES
from .characteristics.dlcs import DLCS
from .characteristics.fan_translations import FAN_TRANSLATIONS
from .characteristics.freeware import FREEWARE
from .characteristics.limited_print_games import LIMITED_PRINT_GAMES
from .characteristics.longest_titles import LONGEST_TITLES
from .characteristics.non_steam import NON_STEAM
from .characteristics.obscure_games import OBSCURE_GAMES
from .characteristics.palindrome import PALINDROME_GAMES
from .characteristics.subscriptions import SUBSCRIPTIONS
from .characteristics.untranslated_games import get_untranslated_games_selector
from .characteristics.virtual_console import VIRTUAL_CONSOLE
from .characteristics.vr import VR

# Companies
from .companies.aaa_games import AAA_GAMES
from .companies.first_party_games import FIRST_PARTY_GAMES
from .companies.fromsoftware import FROMSOFTWARE
from .companies.major_indie_games import get_major_indie_games_selector

# Concepts
from .concepts.alternate_editions import get_alternate_editions_selector
from .concepts.backloggd_top import get_backloggd_top_selector
from .concepts.horror_games import get_horror_games_selector
from .concepts.third_party_selectors import get_third_party_selector

# Genres
from .genre.genre_selectors import get_genre_selector, get_multi_genre_selector
from .genre.visual_novels import VISUAL_NOVELS

# Personal
from .personal.birthday_games import BIRTHDAY_GAMES
from .personal.dad_games import DAD_GAMES
from .personal.favorites import get_favorites_selector
from .personal.franchise_playthroughs import (
    FRANCHISE_CONTENDERS,
    get_franchise_playthroughs_selector,
)
from .personal.max_priority import MAX_PRIORITY
from .personal.physical_games import PHYSICAL_GAMES
from .personal.zach_games import ZACH_GAMES

# Playtime
from .playtime.longest_games import LONGEST_GAMES
from .playtime.playtime_selectors import (
    get_playtime_selector,
    NO_ESTIMATED_PLAYTIME,
    PlaytimeBounds,
)
from .playtime.shortest_games import (
    get_shortest_by_selector,
    SHORTEST_GAMES,
    SHORTEST_OVERALL,
    SHORTEST_OVERALL_UNCOMMON_GENRE,
)
from .playtime.under_1_hour_uncommon_genre import UNDER_1_HOUR_UNCOMMON_GENRE

# Progress
from .progress.all_games import ALL_GAMES
from .progress.challenge_selectors import (
    get_alphabetical_first_letter,
    get_one_per_criteria_challenge_selector,
    get_platform_completion_id,
    get_playtime,
    get_top_developers,
)
from .progress.incomplete_collections import get_incomplete_collections_selector
from .progress.now_playing import get_now_playing_selector
from .progress.percentiles import get_percentiles_selector, group_by_percentile
from .progress.platform_progress import get_platform_progress_selector
from .progress.unplayed_purchases import UNPLAYED_PURCHASES
from .progress.unplayed_wishlisted import get_unplayed_wishlisted_selector
from .progress.zero_percent import get_zero_percent_selector

# Rating
from .rating.best_by_selectors import get_best_by_selector
from .rating.best_companies_by_metacritic import BEST_COMPANIES_BY_METACRITIC
from .rating.best_years_by_metacritic import BEST_YEARS_BY_METACRITIC
from .rating.big_games import BIG_GAMES
from .rating.highest_priority_platforms import HIGHEST_PRIORITY_PLATFORMS
from .rating.high_critic_ratings import HIGH_CRITIC_RATINGS
from .rating.high_priority_ratings import HIGH_PRIORITY_RATINGS
from .rating.high_user_ratings import HIGH_USER_RATINGS
from .rating.top_games import TOP_GAMES
from .rating.underprioritized import UNDERPRIORITIZED
from .rating.very_bad_games import VERY_BAD_GAMES
from .rating.very_positive_games import VERY_POSITIVE_GAMES

# Statistics
from .statistics.completed_values import get_completed_values_selector
from .statistics.games_on_order import get_games_on_order_selector
from .statistics.largest_rating_differences import (
    get_largest_rating_differences_selector,
)
from .statistics.most_played_selectors import get_most_played_selector
from .statistics.played_purchases import get_played_purchases_selector
from .statistics.purchase_to_completion_gaps import (
    get_purchase_to_completion_gaps_selector,
)
from .statistics.quarterly_spend import get_quarterly_spend_selector
from .statistics.unknown_playability import get_unknown_playability_selector
from .statistics.unordered_amazon_games import get_unordered_amazon_games_selector
from .statistics.unowned_pc_games import get_unowned_pc_games_selector
from .statistics.unplayable_high_priority import get_unplayable_high_priority_selector
from .statistics.unplayable_low_priority import get_unplayable_low_priority_selector
from .statistics.will_not_play import get_will_not_play_selector
from .statistics.most_concurrent_playthroughs import (
    get_most_concurrent_playthroughs_selector,
)
from .statistics.longest_playthroughs import get_longest_playthroughs_selector

# Validations
from .validations.completed_ordering import get_completed_ordering_selector
from .validations.missing_playtime import get_missing_playtime_selector
from .validations.misspellings import MISSPELLINGS
from .validations.non_downloaded_games import get_non_downloaded_games_selector
from .validations.potential_duplicates import POTENTIAL_DUPLICATES
from .validations.sheet_validations import get_sheet_validations_selector
