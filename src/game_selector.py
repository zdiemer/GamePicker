from __future__ import annotations

import os
from typing import Any, Callable, List, Optional, Set

from excel_game import ExcelGame
from excel_backed_cache import ExcelBackedCache
from game_grouping import GameGrouping, GameGroups
from picked_game import PickedGame
from picker_enums import PickerMode


class GameSelector:
    selector: Optional[Callable[[List[ExcelGame]], List[ExcelGame]]]
    name: Optional[str]
    grouping: GameGrouping
    sort: Optional[Callable[[PickedGame], Any]]
    include_platform: bool
    reverse_sort: bool
    filter: Optional[Callable[[ExcelGame], bool]]
    custom_prefix: Optional[Callable[[ExcelGame], str]]
    custom_suffix: Optional[Callable[[ExcelGame], str]]
    get_description: Optional[Callable[[GameGroups], str]]
    no_cache: bool
    mode: PickerMode
    include_in_picks: bool
    skip_unless_specified: bool
    group_count: Optional[int]
    run_on_modes: Set[PickerMode]
    games: Optional[List[ExcelGame]]
    no_force: bool
    enabled: bool

    _internal_sort: Optional[Callable[[PickedGame], Any]]
    _cache: ExcelBackedCache
    CACHE_FOLDER = "caches"

    def __init__(
        self,
        selector: Optional[Callable[[List[ExcelGame]], List[ExcelGame]]] = None,
        name: Optional[str] = None,
        grouping: Optional[GameGrouping] = None,
        sort: Optional[Callable[[PickedGame], Any]] = None,
        include_platform: Optional[bool] = None,
        reverse_sort: bool = False,
        _filter: Optional[Callable[[ExcelGame], bool]] = None,
        custom_prefix: Optional[Callable[[ExcelGame], str]] = None,
        custom_suffix: Optional[Callable[[ExcelGame], str]] = None,
        get_description: Optional[Callable[[GameGroups], str]] = None,
        no_cache: bool = False,
        mode: PickerMode = PickerMode.ALL,
        include_in_picks: bool = True,
        skip_unless_specified: bool = False,
        group_count: Optional[int] = None,
        run_on_modes: Set[PickerMode] = set([]),
        games: Optional[List[ExcelGame]] = None,
        no_force: bool = False,
        enabled: bool = True,
    ):
        if selector is None and name is None:
            raise ValueError("Must specify a name when not specifying a selector")

        if name is None and selector is not None and selector.__name__ == "<lambda>":
            raise ValueError("Must have a name for a lambda selector")

        self.selector = selector
        self.name = name or selector.__name__.replace("_", " ").strip().title()
        self.grouping = grouping or GameGrouping()
        self._internal_sort = sort
        self.sort = self.__get_sort()
        self.include_platform = (
            include_platform is None and grouping is not None
        ) or include_platform
        self.reverse_sort = reverse_sort
        self.filter = _filter
        self.custom_prefix = custom_prefix or self.__default_prefix_suffix
        self.custom_suffix = custom_suffix or self.__default_prefix_suffix
        self.get_description = get_description
        self.no_cache = no_cache
        self.mode = mode
        self.include_in_picks = include_in_picks
        self.skip_unless_specified = skip_unless_specified
        self.group_count = group_count
        self.run_on_modes = run_on_modes
        self.games = games
        self.no_force = no_force
        self.enabled = enabled

        self.grouping.set_selection_sort(self.sort, self.reverse_sort)
        self._cache = ExcelBackedCache()

    def __get_sort(self) -> Callable[[PickedGame], Any]:
        def default_sort(g: PickedGame):
            sort_by_values = (
                g.game.normal_title,
                g.game.release_date,
                g.game.combined_rating,
            )

            if self._internal_sort is not None:
                return (self._internal_sort(g), sort_by_values)

            return sort_by_values

        return default_sort

    def __default_prefix_suffix(self, _):
        return ""

    def select(self, games: List[ExcelGame]) -> List[ExcelGame]:
        selection: Optional[List[ExcelGame]] = None

        if any(self.run_on_modes) and self.mode not in self.run_on_modes:
            return []

        if not self.no_cache:
            selection = self._cache.load(self.get_cache_full_path())

        if selection is not None:
            return selection

        if self.selector is None and self.filter is not None:
            self.selector = lambda gs: list(filter(self.filter, gs))

        selection = (
            self.selector(self.games or games)
            if self.selector is not None
            else self.games or games
        )
        self.__write_cache(selection)

        return selection

    def select_groups(self, games: List[ExcelGame], _sorted: bool = True) -> GameGroups:
        groups = self.grouping.get_groups(self.select(games), _sorted=True)

        if _sorted:
            for key, group in groups.items():
                groups[key] = sorted(group, key=self.sort, reverse=self.reverse_sort)[
                    : self.grouping.group_size
                ]

                if self.grouping.group_size is not None and self.grouping.should_rank:
                    # May need to elect a new highest priority game
                    highest: Optional[PickedGame] = None

                    for g in groups[key]:
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

        return groups

    def __get_file_name_base(self) -> str:
        return f'{self.name.lower().replace(" ", "_")}'

    def get_output_file_name(self) -> str:
        return f"{self.__get_file_name_base()}.txt"

    def get_cache_file_name(self) -> str:
        return f"cache-{self.__get_file_name_base()}.pkl"

    def get_cache_full_path(self) -> str:
        return f"{self.CACHE_FOLDER}\\{self.mode.name.lower()}\\{self.get_cache_file_name()}"

    def __write_cache(self, selections: List[ExcelGame]):
        if not os.path.exists(self.CACHE_FOLDER):
            os.mkdir(self.CACHE_FOLDER)
        if not os.path.exists(f"{self.CACHE_FOLDER}\\{self.mode.name.lower()}"):
            os.mkdir(f"{self.CACHE_FOLDER}\\{self.mode.name.lower()}")

        self._cache.write(self.get_cache_full_path(), selections)
