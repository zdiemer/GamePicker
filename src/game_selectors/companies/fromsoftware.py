from game_selector import GameSelector

FROMSOFTWARE = GameSelector(
    _filter=lambda game: game.developer.strip() == "FromSoftware"
    or game.publisher.strip() == "FromSoftware",
    name="FromSoftware",
)
