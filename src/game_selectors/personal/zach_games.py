import itertools

from game_selector import GameSelector


ZACH_GAMES = GameSelector(
    _filter=lambda g: any(
        x in y
        for x, y in itertools.product(
            ["zach", "zack", "zak", "zac", "zax"],
            [
                g.normal_title,
                g.developer.lower(),
                g.publisher.lower(),
            ],
        )
    ),
    name="Zach Games",
)
