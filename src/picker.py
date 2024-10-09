import datetime
import warnings

from typing import List

import click

from picker_enums import PickerMode
from game_picker import GamesPicker


@click.command()
@click.option(
    "--mode",
    "-m",
    type=str,
    default="all",
    help="Selects the picker mode, which limits valid platforms",
)
@click.option(
    "--out",
    "-o",
    type=bool,
    default=False,
    is_flag=True,
    help="If specified, saves output as text files for given mode",
)
@click.option(
    "--update_all",
    "-u",
    type=bool,
    default=False,
    is_flag=True,
    help="Regenerates all output text files for all modes",
)
@click.option(
    "--no_cache",
    "-nc",
    type=bool,
    default=False,
    is_flag=True,
    help="Ignores the cache file",
)
@click.option(
    "--selector",
    "-s",
    type=str,
    help="If specified, runs only the specified selector",
    multiple=True,
)
@click.option(
    "--list_selectors",
    "-ls",
    type=bool,
    default=False,
    is_flag=True,
    help="Lists all available selectors",
)
@click.option(
    "--search",
    "-sr",
    type=str,
    default="",
    help="Searches for a given game in the sheet",
)
@click.option(
    "--page",
    "-p",
    type=int,
    default=1,
    help="Search page",
)
@click.option(
    "--completion",
    "-c",
    type=bool,
    default=False,
    is_flag=True,
    help="Displays total completion",
)
@click.option(
    "--no_diff",
    "-nd",
    type=bool,
    default=False,
    is_flag=True,
    help="Skips file diffs when updating",
)
@click.option(
    "--platform",
    "-pl",
    type=str,
    default=None,
    help="Limits picks to a given platform",
)
@click.option(
    "--force",
    "-f",
    type=bool,
    default=False,
    is_flag=True,
    help="Forces running selectors marked as skip_unless_specified",
)
def main(
    mode: str,
    out: bool,
    update_all: bool,
    no_cache: bool,
    selector: List[str],
    list_selectors: bool,
    search: str,
    page: int,
    completion: bool,
    no_diff: bool,
    platform: str,
    force: bool,
):
    start = datetime.datetime.now()
    try:
        mode = PickerMode[mode.upper()]
    except KeyError:
        print(
            f"Invalid mode. Valid options are {', '.join(p.name.lower() for p in list(PickerMode))}."
        )
        return

    selectors = list(sel.lower() for sel in selector)

    gp = GamesPicker(mode, no_cache)

    if completion:
        gp.completion()
        return

    if search:
        gp.search(search, page - 1)
        return

    if list_selectors:
        for sel in gp.get_selectors():
            print(sel.name)
        return

    if update_all:
        for p in list(PickerMode):
            gp.with_mode(p).pick_game(selectors, True, no_diff, force=force)

        print(f"Took {datetime.datetime.now() - start} to update all outputs.")
        return

    game = gp.pick_game(selectors, out, no_diff, platform, force)

    print(f"Picked {game} in {datetime.datetime.now() - start}")


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    # pylint: disable=no-value-for-parameter
    main()
