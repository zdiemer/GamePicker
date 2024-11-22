from game_selector import GameSelector


VERY_BAD_GAMES = GameSelector(
    _filter=lambda game: game.combined_rating < 0.4,
    name="Very Bad Games",
    custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
    sort=lambda g: g.game.combined_rating,
)
