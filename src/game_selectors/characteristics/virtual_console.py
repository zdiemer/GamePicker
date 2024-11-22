from game_selector import GameSelector

VIRTUAL_CONSOLE = GameSelector(
    _filter=lambda g: g.digital_platform == "Virtual Console",
    name="Virtual Console",
)
