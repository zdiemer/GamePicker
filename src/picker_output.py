import copy
from typing import Dict, Iterator, List, Optional

from game_grouping import GameGrouping
from game_selector import GameSelector
from picked_game import PickedGame
from picker_enums import PickerMode

BASE_DROPBOX_FOLDER: str = "C:\\Users\\zachd\\Dropbox\\Video Game Lists"
PICKER_OUTPUT_PATH: str = "picker_out"


def get_output_path(mode: PickerMode) -> str:
    return f"{BASE_DROPBOX_FOLDER}\\{PICKER_OUTPUT_PATH}\\{mode.name.lower()}"


def get_group_output(
    output: str,
    group_name: str,
    group: List[PickedGame],
    name_collisions: Dict[str, int],
    selector: GameSelector,
    grouping: GameGrouping,
    level: int = 0,
):
    spacer = "    "

    output += f"{spacer * level}{group_name}:\n\n"

    if len(selector.grouping.subgroupings) == level:
        games: List[PickedGame] = sorted(
            group, key=selector.sort, reverse=selector.reverse_sort
        )[: grouping.take]

        if grouping.take is not None:
            # May need to elect a new highest priority game
            highest: Optional[PickedGame] = None

            for g in games:
                if highest is None:
                    highest = g
                elif g.highest_priority:
                    highest = g
                    break
                elif g.game.combined_rating > highest.game.combined_rating or (
                    g.game.combined_rating == highest.game.combined_rating
                    and g.game.normal_title > highest.game.normal_title
                ):
                    highest = g

            highest.highest_priority = True

        def get_game_string(g: PickedGame) -> str:
            with_year = (
                g.game.game_platform_hash_id in name_collisions
                and name_collisions[g.game.game_platform_hash_id] > 1
            )

            return g.as_str(
                selector.include_platform,
                selector.custom_prefix(g.game),
                selector.custom_suffix(g.game),
                with_year=with_year,
            )

        output += (
            "\n".join(f"{spacer * (level + 1)}{get_game_string(g)}" for g in games)
            + "\n\n"
        )

    return output


def get_subgrouping_output(
    subgroupings: Iterator[GameGrouping],
    subgrouping: Optional[GameGrouping],
    group: List[PickedGame],
    level: int,
    selector: GameSelector,
    output: str,
    name_collisions: Dict[str, int],
):
    if subgrouping is None:
        return output

    next_sg = next(subgroupings, None)

    for group_name, sgroup in subgrouping.get_groups(
        [g.game for g in group], _sorted=True
    ).items():
        group_name = subgrouping.get_group_name((group_name, sgroup))
        output = get_group_output(
            output,
            group_name,
            sgroup,
            name_collisions,
            selector,
            subgrouping,
            level,
        )
        output = get_subgrouping_output(
            copy.deepcopy(subgroupings),
            next_sg,
            sgroup,
            level + 1,
            selector,
            output,
            name_collisions,
        )

    return output
