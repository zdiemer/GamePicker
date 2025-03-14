from typing import Any, List, Tuple
import datetime

from game_grouping import GameGrouping
from game_selector import GameSelector
from picked_game import PickedGame
from picker_enums import PickerMode


def get_group_name(kvp: Tuple[Any, List[PickedGame]]) -> str:
    purchase_date, games = kvp

    # Set typing hints
    purchase_date: datetime.datetime = purchase_date

    total_purchase_price = sum(g.game.purchase_price for g in games)

    return f'{purchase_date.strftime("%b, %Y")} (${total_purchase_price:.2f})'


UNPLAYED_PURCHASES = GameSelector(
    _filter=lambda game: game.owned
    and game.date_purchased is not None
    and (game.purchase_price or 0) > 0,
    name="Unplayed Purchases",
    grouping=GameGrouping(
        lambda g: datetime.datetime(g.date_purchased.year, g.date_purchased.month, 1),
        reverse=True,
        get_group_name=get_group_name,
    ),
    custom_prefix=lambda g: f"{g.date_purchased.strftime('%m/%d: ')}",
    custom_suffix=lambda g: f" - ${g.purchase_price:0.2f}",
    sort=lambda g: (g.game.date_purchased, g.game.normal_title),
    reverse_sort=True,
    run_on_modes=set([PickerMode.ALL]),
)
