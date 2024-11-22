from game_selector import GameSelector

DLCS = GameSelector(_filter=lambda game: game.dlc, name="DLCs")
