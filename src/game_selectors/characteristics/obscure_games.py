from game_selector import GameSelector


OBSCURE_GAMES = GameSelector(
    _filter=lambda game: game.gamefaqs_rating is None
    and game.metacritic_rating is None,
    name="Obscure Games",
)
