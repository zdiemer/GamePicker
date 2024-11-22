from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def get_games_on_order_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        games=data_provider.get_games_on_order(),
        name="Games on Order",
        include_platform=False,
        grouping=GameGrouping(
            lambda g: g.order_vendor,
            subgroupings=[GameGrouping(should_rank=False)],
            custom_suffix=lambda kvp: f" - ${sum(g.game.purchase_price for g in kvp[1]):,.2f}",
            should_rank=False,
        ),
        include_in_picks=False,
        run_on_modes=set([PickerMode.ALL]),
        custom_suffix=lambda g: f" (${g.purchase_price:.2f})",
    )
