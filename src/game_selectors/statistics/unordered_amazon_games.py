from typing import List
import logging

import asyncio

from clients import AmazonClient
from excel_game import ExcelGame, ExcelGameBuilder

from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


async def unordered_amazon_games(data_provider: DataProvider) -> List[ExcelGame]:
    logging.basicConfig(level=logging.DEBUG)

    amazon_client = AmazonClient(
        data_provider.get_validator(), pages_without_unreleased_threshold=20
    )

    unordered_games = await amazon_client.get_unordered_games()

    return [
        ExcelGameBuilder()
        .with_title(uo.title)
        .with_platform(p)
        .with_release_date(uo.release_date)
        .with_purchase_price(uo.price)
        .with_order_link(uo.url)
        .build()
        for p, p_games in unordered_games.items()
        for uo in p_games
    ]


def get_unordered_amazon_games_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        lambda _: asyncio.run(unordered_amazon_games(data_provider)),
        name="Unordered Amazon Games",
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
        skip_unless_specified=True,
        no_force=True,
        custom_suffix=lambda g: f" - ${g.purchase_price:,.2f} ({g.order_link})",
        include_platform=False,
        grouping=GameGrouping(should_rank=False),
    )
