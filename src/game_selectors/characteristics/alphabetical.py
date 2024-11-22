from game_grouping import GameGrouping
from game_selector import GameSelector


ALPHABETICAL = GameSelector(
    lambda gs: sorted(
        gs,
        key=lambda game: game.normal_title,
    ),
    name="Alphabetical",
    grouping=GameGrouping(
        lambda g: (
            g.normal_title[0].capitalize()
            if g.normal_title[0].isalpha()
            else "#" if g.normal_title[0].isdigit() else "?"
        )
    ),
)
