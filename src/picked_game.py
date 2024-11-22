from picker_constants import PLATFORM_SHORT_NAMES
from excel_game import ExcelGame


class PickedGame:
    game: ExcelGame
    high_priority: bool
    highest_priority: bool
    selection_name: str = ""

    def __init__(
        self,
        game: ExcelGame,
        high_priority: bool = False,
        highest_priority: bool = False,
    ):
        self.game = game
        self.high_priority = high_priority
        self.highest_priority = highest_priority

    def as_str(
        self,
        with_platform: bool = True,
        prefix: str = "",
        suffix: str = "",
        with_year: bool = False,
        markdown: bool = False,
    ) -> str:
        p_short_name = PLATFORM_SHORT_NAMES[self.game.platform]

        platform_str = f" ({p_short_name})" if with_platform else ""

        playtime_str = ""

        year_str = f" ({self.game.release_year or 'Unreleased'})" if with_year else ""

        if self.game.estimated_playtime is not None:
            left = "[" if with_platform else "("
            right = "]" if with_platform else ")"

            playtime_str += f" {left}"

            if self.game.estimated_playtime < 1:
                playtime_str += f"{int(self.game.estimated_playtime * 60)}min"
            else:
                playtime_str += (
                    f"{self.game.estimated_playtime:0.1f}"
                    if int(self.game.estimated_playtime) != self.game.estimated_playtime
                    else f"{int(self.game.estimated_playtime)}"
                ) + "hr"
            playtime_str += right

        selection_str = f" {{{self.selection_name}}}" if self.selection_name else ""

        priority_str = (
            (
                f"{'*' if self.high_priority else ''}"
                f"{'^' if self.highest_priority else ''}"
            )
            if not markdown
            else ""
        )

        high_pri_wrapper = "**" if self.high_priority else ""
        highest_pri_wrapper = "*" if self.highest_priority else ""

        wrapper = high_pri_wrapper + highest_pri_wrapper

        game_str = (
            f"{prefix}{self.game.title}{priority_str}{year_str}{platform_str}"
            f"{playtime_str}{selection_str}{suffix}"
        )

        return game_str if not markdown else f"{wrapper}{game_str}{wrapper}"

    def __str__(self) -> str:
        return self.as_str()

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.game)
