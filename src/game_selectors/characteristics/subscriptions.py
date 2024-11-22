from game_grouping import GameGrouping
from game_selector import GameSelector

SUBSCRIPTIONS = GameSelector(
    _filter=lambda game: game.subscription_service is not None,
    name="Subscriptions",
    grouping=GameGrouping(
        lambda g: g.subscription_service,
        subgroupings=[GameGrouping(lambda g: g.platform)],
    ),
    include_platform=False,
    include_in_picks=False,
)
