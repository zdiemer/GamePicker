from game_selector import GameSelector

FREEWARE = GameSelector(
    _filter=lambda game: game.notes is not None and game.notes.strip() == "Freeware",
    include_in_picks=False,
    name="Freeware",
)
