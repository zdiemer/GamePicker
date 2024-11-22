from game_selector import GameSelector

VERY_POSITIVE_GAMES = GameSelector(
    _filter=lambda game: game.combined_rating >= 0.8,
    name="Very Positive Games",
    custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
    sort=lambda g: g.game.combined_rating,
    reverse_sort=True,
)
