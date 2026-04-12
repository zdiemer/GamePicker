from typing import List, Tuple

from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picked_game import PickedGame
from picker_enums import PickerMode


def get_backlog_group_suffix(kvp: Tuple[str, List[PickedGame]]):
    count_completed = sum(1 for pg in kvp[1] if pg.game.group_metadata == "Finished")
    count_purchased = sum(1 for pg in kvp[1] if pg.game.group_metadata == "Purchased")
    total_cost = sum(pg.game.purchase_price or 0 for pg in kvp[1])

    incomplete = count_purchased - count_completed

    suffix = f" (${total_cost:.2f})"

    if incomplete > 0:
        suffix += f" - {incomplete} purchase{'s' if incomplete != 1 else ''} behind"
    elif incomplete < 0:
        suffix += f" - {abs(incomplete)} purchase{'s' if incomplete != 1 else ''} ahead"
    else:
        suffix += " - Even with purchases!"

    return suffix


def get_purchase_backlog_selector(data_provider: DataProvider) -> GameSelector:
    completed_games = list(
        map(
            lambda g: g.get_copy_with_metadata("Finished"),
            filter(
                lambda g: g.completed and g.date_completed is not None,
                data_provider.get_games(),
            ),
        )
    )

    purchased_games = list(
        map(
            lambda g: g.get_copy_with_metadata("Purchased"),
            filter(
                lambda g: g.date_purchased is not None,
                data_provider.get_games() + data_provider.get_games_on_order(),
            ),
        )
    )

    return GameSelector(
        name="Purchase Backlog",
        grouping=GameGrouping(
            lambda g: g.date_completed.strftime("%B %Y")
            if g.group_metadata == "Finished"
            else g.date_purchased.strftime("%B %Y"),
            sort=lambda kvp: min(
                (
                    pg.game.date_completed
                    if pg.game.group_metadata == "Finished"
                    else pg.game.date_purchased
                )
                for pg in kvp[1]
            ),
            custom_suffix=get_backlog_group_suffix,
            subgroupings=[
                GameGrouping(
                    lambda g: g.group_metadata,
                    should_rank=False,
                )
            ],
            reverse=True,
        ),
        custom_suffix=lambda g: f" - ${g.purchase_price or 0:.2f}"
        if g.date_purchased is not None
        else "",
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
        games=completed_games + purchased_games,
    )
