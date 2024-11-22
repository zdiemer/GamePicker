from game_selector import GameSelector

BIRTHDAY_GAMES = GameSelector(
    _filter=lambda g: g.release_date.month == 4 and g.release_date.day == 5,
    name="Birthday Games",
    custom_suffix=lambda g: f" [{g.release_year}]",
)
