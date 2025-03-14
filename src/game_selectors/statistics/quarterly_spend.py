from typing import List, Tuple
import datetime
from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picked_game import PickedGame
from picker_enums import PickerMode


def get_year_and_quarter(date: datetime.datetime) -> str:
    quarter = 4

    if date.month in (1, 2, 3):
        quarter = 1
    elif date.month in (4, 5, 6):
        quarter = 2
    elif date.month in (7, 8, 9):
        quarter = 3

    return f"Q{quarter} {date.year}"


def get_group_name(kvp: Tuple[str, List[PickedGame]]) -> str:
    purchase_quarter, games = kvp

    total_purchase_price = sum(g.game.purchase_price for g in games)

    return f"{purchase_quarter} (${total_purchase_price:,.2f})"


def get_quarterly_spend_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        name="Quarterly Spend",
        grouping=GameGrouping(
            lambda g: get_year_and_quarter(g.date_purchased),
            should_rank=False,
            get_group_name=get_group_name,
            sort=lambda kvp: min(pg.game.date_purchased for pg in kvp[1]),
            reverse=True,
        ),
        _filter=lambda g: g.date_purchased is not None and (g.purchase_price or 0) > 0,
        custom_suffix=lambda g: f" - ${g.purchase_price:.2f}",
        include_in_picks=False,
        run_on_modes=set([PickerMode.ALL]),
        games=data_provider.get_games() + data_provider.get_games_on_order(),
    )
