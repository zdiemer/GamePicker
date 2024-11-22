from game_grouping import GameGrouping
from game_selector import GameSelector

TOP_GAMES = GameSelector(
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
)
