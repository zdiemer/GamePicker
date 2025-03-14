from __future__ import annotations

import datetime
import math
import os
import random
from difflib import SequenceMatcher, unified_diff
from typing import List, Optional, Set, Tuple

from excel_game import ExcelGame

from logging_decorator import LoggingColor, LoggingDecorator


import picker_output
from data_provider import DataProvider
from excel_filter import ExcelFilter
from game_selector import GameSelector
from picked_game import PickedGame
from picker_constants import PLATFORM_SHORT_NAMES
from picker_enums import PickerMode
from selector_library import SelectorLibrary


class GamesPicker:
    _data_provider: DataProvider
    _library: SelectorLibrary
    _mode: PickerMode

    __BASE_OUTPUT_PATH = "picker_out"
    __BASE_DROPBOX_FOLDER = "C:\\Users\\zachd\\Dropbox\\Video Game Lists"

    def __init__(self, mode: PickerMode = PickerMode.ALL, no_cache: bool = False):
        self._mode = mode
        self._no_cache = no_cache
        self._data_provider = DataProvider(self._no_cache)
        self._library = SelectorLibrary(self._data_provider, self._mode)

    def __cleanup(self):
        files_to_remove = []
        expected_files = []
        expected_cache_files = []

        cache_folder = f"{GameSelector.CACHE_FOLDER}\\{self._mode.name.lower()}"

        for selector in self.get_selectors():
            expected_files.append(selector.get_output_file_name())
            expected_cache_files.append(selector.get_cache_file_name())

        for root, _, files in os.walk(picker_output.get_output_path(self._mode)):
            for file in files:
                if file not in expected_files:
                    files_to_remove.append(os.path.join(root, file))
            break

        for root, _, files in os.walk(cache_folder):
            for file in files:
                if file not in expected_cache_files:
                    files_to_remove.append(os.path.join(root, file))
            break

        for file in files_to_remove:
            os.remove(file)
            print(f"Cleaned up {file}")

    def get_selectors(self) -> List[GameSelector]:
        selectors = self._library.all()

        for selector in selectors:
            selector.no_cache = self._no_cache
            selector.mode = self._mode

        return sorted(
            list(filter(lambda s: s.enabled, selectors)),
            key=lambda s: s.name.casefold(),
        )

    def with_mode(self, mode: PickerMode) -> GamesPicker:
        self._mode = mode
        self._library.update_mode(self._mode)
        return self

    def run_selector(
        self,
        selector: GameSelector,
        games: List[ExcelGame],
        write_output: bool = False,
        no_diff: bool = False,
        force_picks: bool = False,
        markdown: bool = True,
    ) -> Set[PickedGame]:
        picks: Set[PickedGame] = set([])

        selection = selector.select(games)

        full_path = picker_output.get_output_path(self._mode)

        if write_output:
            if not os.path.exists(
                f"{self.__BASE_DROPBOX_FOLDER}\\{self.__BASE_OUTPUT_PATH}"
            ):
                os.mkdir(f"{self.__BASE_DROPBOX_FOLDER}\\{self.__BASE_OUTPUT_PATH}")
            if not os.path.exists(full_path):
                os.mkdir(full_path)

        groups = selector.grouping.get_groups(selection, _sorted=True)

        output = (
            selector.get_description(groups) + "\n\n"
            if selector.get_description is not None and any(selection) and write_output
            else ""
        )

        g_count = 0

        for group_name, group in groups.items():
            if selector.group_count is not None and g_count > selector.group_count - 1:
                break
            g_count += 1
            level = 0
            group_name = selector.grouping.get_group_name((group_name, group))

            if write_output:
                output = picker_output.get_group_output(
                    output,
                    group_name,
                    group,
                    self._data_provider.get_name_collisions(),
                    selector,
                    selector.grouping,
                    level,
                    markdown,
                )

                subgrouping_iter = iter(selector.grouping.subgroupings)
                next_sg = next(subgrouping_iter, None)
                output = picker_output.get_subgrouping_output(
                    subgrouping_iter,
                    next_sg,
                    group,
                    level + 1,
                    selector,
                    output,
                    self._data_provider.get_name_collisions(),
                    markdown,
                )
            if selector.include_in_picks or force_picks:
                for pick in group:
                    pick.selection_name = selector.name
                picks = picks.union(set(group))

        output = output.strip()
        file_name = f"{full_path}\\{selector.get_output_file_name()}"
        if any(output):
            was_created = False

            if not os.path.isfile(file_name):
                with open(file_name, "w", encoding="utf-8") as f:
                    print(f"Created {file_name}")
                    was_created = True

            with open(file_name, "r+", encoding="utf-8") as f:
                og_f_lines = []
                o_lines = []
                diff_lines = []

                if not was_created:
                    og_f_lines = f.read().splitlines()
                    o_lines = output.splitlines()

                    diff_lines = list(
                        unified_diff(
                            og_f_lines,
                            o_lines,
                            fromfile=file_name,
                            tofile=f"Updated {file_name}",
                            lineterm="",
                            n=0,
                        )
                    )

                if was_created or any(diff_lines):
                    f.seek(0)
                    f.write(output)
                    f.truncate()

                    if was_created or no_diff:
                        return picks

                    for line in diff_lines:
                        printed = False
                        for prefix in ("---", "+++", "@@"):
                            if line.startswith(prefix):
                                print(line)
                                printed = True
                        if printed:
                            continue

                        if line.startswith("-"):
                            print(LoggingDecorator.as_color(line, LoggingColor.RED))
                        elif line.startswith("+"):
                            print(LoggingDecorator.as_color(line, LoggingColor.GREEN))
        elif not any(output) and write_output and os.path.isfile(file_name):
            os.remove(file_name)
            print(f"Completed {file_name}!")

        return picks

    def pick_game(
        self,
        selector_names: Optional[List[str]] = None,
        write_output: bool = False,
        no_diff: bool = False,
        platform: Optional[str] = None,
        force: bool = False,
        markdown: bool = True,
    ) -> PickedGame:
        if len(PLATFORM_SHORT_NAMES) != len(set(PLATFORM_SHORT_NAMES.values())):
            raise KeyError("Duplicate short name in PLATFORM_SHORT_NAMES")

        unplayed = list(
            filter(
                lambda g: (
                    platform is None
                    or self._data_provider.get_validator().titles_equal_normalized(
                        platform, g.platform.value
                    )
                )
                and ExcelFilter.included_in_mode(g, self._mode),
                self._data_provider.get_unplayed_candidates(),
            )
        )

        picks: Set[PickedGame] = set()
        selectors = self.get_selectors()

        if selector_names and any(selector_names):
            selectors = list(
                filter(lambda s: s.name.lower().strip() in selector_names, selectors)
            )

            if not any(selectors):
                raise ValueError("One or more invalid selector name")

        valid_selectors = []

        for selector in selectors:
            should_skip = selector.skip_unless_specified

            if platform:
                selector.no_cache = True

            start = datetime.datetime.now()

            if force and not selector.no_force:
                should_skip = False

            if ((not selector_names or not any(selector_names)) and should_skip) or (
                not selector.include_in_picks and not write_output
            ):
                continue

            valid_selectors.append(selector)

            picks = picks.union(
                self.run_selector(
                    selector, unplayed, write_output, no_diff, markdown=markdown
                )
            )

            if selector.skip_unless_specified and force and not selector.no_force:
                print(f"Forcing {selector.name} took {datetime.datetime.now() - start}")

        if write_output:
            self.__cleanup()

        return random.choice(list(picks)) if any(picks) else None

    def search(self, title: str, p: int = 0) -> ExcelGame:
        matches: List[Tuple[ExcelGame, float]] = []

        def search_impl(_games: List[ExcelGame], source: str = ""):
            for game in _games:
                t1 = self._data_provider.get_validator().normalize(title)
                t2 = self._data_provider.get_validator().normalize(game.title)
                rat = SequenceMatcher(
                    None,
                    t1,
                    t2,
                ).ratio()

                contained = t1 in t2
                if rat >= 0.76 or contained:
                    game.title += " (Owned)" if game.owned else ""
                    if any(source):
                        game.title = f"{game.title} ({source})"
                    game.compute_properties()
                    matches.append((game, rat, contained))

        search_impl(self._data_provider.get_games())
        search_impl(self._data_provider.get_games_on_order(), "Games on Order")

        sorted_matches = sorted(matches, key=lambda t: (t[2], t[1]), reverse=True)

        for game, _, _ in sorted_matches[10 * p : 10 * (p + 1)]:
            print(game.full_name)
        if any(sorted_matches[10 * (p + 1) :]):
            num_rem = len(sorted_matches[10 * (p + 1) :])
            print(f"{num_rem} more match{'' if num_rem == 1 else 'es'}, use -p to page")
        pages = math.ceil(len(sorted_matches) / 10)
        first_pages = " ".join(
            (
                str(i)
                if p + 1 != i
                else LoggingDecorator.as_color(str(i), LoggingColor.GREEN)
            )
            for i in range(1, min(6, pages + 1))
        )
        last_pages = ""
        highlighted_slice = " ... " if pages > 10 else " " if pages > 5 else ""
        if p + 1 > 5 and p + 1 < pages - 5:
            leading_elip = " ... " if p + 1 > 8 else " "
            trailing_elip = " ... " if p + 1 < pages - 8 else " "
            slice_port = " ".join(
                (
                    str(i)
                    if p + 1 != i
                    else LoggingDecorator.as_color(str(i), LoggingColor.GREEN)
                )
                for i in range(max(6, p - 1), min(74, p + 4))
            )
            highlighted_slice = f"{leading_elip}{slice_port}{trailing_elip}"
        if pages > 5:
            last_pages = f"{' '.join(str(i) if p + 1 != i else LoggingDecorator.as_color(str(i), LoggingColor.GREEN) for i in range(max(6, pages - 5), pages + 1))}"
        if not any(first_pages):
            first_pages = "No Results"
        print(f"<{first_pages}{highlighted_slice}{last_pages}>")

    def completion(self, purchased_only: bool = False):
        incomplete_games = list(
            filter(
                lambda g: ExcelFilter.included_in_mode(g, self._mode)
                and (not purchased_only or (g.purchase_price or 0) > 0),
                self._data_provider.get_unplayed_candidates(),
            )
        )

        complete_games = list(
            filter(
                lambda g: not purchased_only or (g.purchase_price or 0) > 0,
                self._data_provider.get_played_games(),
            )
        )

        complete = len(complete_games) / (len(incomplete_games) + len(complete_games))

        hr_rem = sum(g.estimated_playtime or 0 for g in incomplete_games)
        daily_hr = 2

        hr_so_far = sum(g.completion_time or 0 for g in complete_games)

        print(
            f"{complete:.02%} ({len(complete_games)}/{len(complete_games)+len(incomplete_games)}) complete ({int(hr_so_far):,}hr). {int(hr_rem):,}hr (or {int(hr_rem / daily_hr):,} days, {int(hr_rem / daily_hr / 7):,} weeks, {int(hr_rem / daily_hr / 7 / 52)} years @ {daily_hr}hr/day) remaining."
        )
