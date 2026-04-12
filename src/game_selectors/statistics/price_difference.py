from typing import List

from data_provider import DataProvider
from game_selector import GameSelector
from game_grouping import GameGrouping
from picker_enums import PickerMode
from game_selectors import get_priced_games


def get_price_difference_selector(data_provider: DataProvider) -> GameSelector:
    def get_price_difference(
        purchase_prices: List[float], current_prices: List[float]
    ) -> float:
        return (sum(c or 0 for c in current_prices) / 100) - sum(
            p or 0 for p in purchase_prices
        )

    def get_price_string(price: float) -> str:
        abs_price = abs(price)
        return f"{'-' if price < 0 else ''}${abs_price:,.2f}"

    return GameSelector(
        get_priced_games,
        games=list(
            filter(lambda g: g.purchase_price is not None, data_provider.get_games())
        ),
        name="Price Difference",
        include_in_picks=False,
        run_on_modes=set([PickerMode.ALL]),
        grouping=GameGrouping(
            should_rank=False,
            get_group_name=lambda kvp: (
                f"{kvp[0]} (${sum(g.game.group_metadata or 0 for g in kvp[1]) / 100:,.2f}, diff: {get_price_string(get_price_difference([g.game.purchase_price for g in kvp[1]], [g.game.group_metadata for g in kvp[1]]))})"
            ),
            sort=lambda kvp: get_price_difference(
                [g.game.purchase_price for g in kvp[1]],
                [g.game.group_metadata for g in kvp[1]],
            ),
            reverse=True,
        ),
        include_platform=False,
        custom_suffix=lambda g: (
            f" - ${(g.group_metadata or 0) / 100:,.2f}, diff: {get_price_string(((g.group_metadata or 0) / 100) - (g.purchase_price or 0))}"
        ),
        sort=lambda g: ((g.game.group_metadata or 0) / 100)
        - (g.game.purchase_price or 0),
        reverse_sort=True,
    )
