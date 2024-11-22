from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional, Tuple

from excel_game import ExcelGame
from picked_game import PickedGame


class GameGroups:
    _grouping: OrderedDict[Any, List[PickedGame]]
    _aggregation: Optional[Dict[Any, Any]]

    def __init__(self, grouping: Dict[Any, List[PickedGame]]):
        self._grouping = grouping
        self._aggregation = None

    def items(self):
        return (
            self._grouping.items()
            if self._aggregation is None
            else self._aggregation.items()
        )

    def keys(self):
        return (
            self._grouping.keys()
            if self._aggregation is None
            else self._aggregation.keys()
        )

    def values(self):
        return (
            self._grouping.values()
            if self._aggregation is None
            else self._aggregation.values()
        )

    def with_agg(
        self, agg: Callable[[List[PickedGame]], Any], inplace: bool = True
    ) -> GameGroups:
        if inplace:
            self._aggregation = {
                key: agg(group) for key, group in self._grouping.items()
            }
            return self

        return GameGroups(self._grouping).with_agg(agg)

    def __contains__(self, i: Any) -> bool:
        return (
            i in self._grouping if self._aggregation is None else i in self._aggregation
        )

    def __delitem__(self, i: Any):
        if self._aggregation is not None:
            del self._aggregation[i]
        else:
            del self._grouping[i]

    def __getitem__(self, i: Any) -> Any | List[PickedGame]:
        return self._grouping[i] if self._aggregation is None else self._aggregation[i]

    def __setitem__(self, i: Any, v: Any):
        if self._aggregation is not None:
            self._aggregation[i] = v
            return

        self._grouping[i] = v

    def __len__(self) -> int:
        return (
            len(self._grouping) if self._aggregation is None else len(self._aggregation)
        )


class GameGrouping:
    grouping: Callable[[ExcelGame], Any]
    sort: Callable[[Tuple[Any, List[PickedGame]]], Any]
    reverse: bool
    subgroupings: List[GameGrouping]
    get_group_name: Optional[Callable[[Tuple[Any, List[PickedGame]]], str]]
    filter: Optional[Callable[[Tuple[Any, List[PickedGame]]], bool]]
    take: Optional[int]
    custom_suffix: Optional[Callable[[Tuple[Any, List[PickedGame]]], str]]
    progress_indicator: Optional[
        Callable[[Tuple[Any, List[PickedGame]]], Tuple[float, float]]
    ]
    priority_determinator: Callable[[ExcelGame, ExcelGame], ExcelGame]
    should_rank: bool

    _selection_sort: Optional[Callable[[PickedGame], Any]]
    _reverse_selection_sort: bool

    def __init__(
        self,
        grouping: Optional[Callable[[ExcelGame], Any]] = None,
        sort: Optional[Callable[[Tuple[Any, List[PickedGame]]], Any]] = None,
        reverse: bool = False,
        subgroupings: Optional[List[GameGrouping]] = None,
        get_group_name: Optional[Callable[[Tuple[Any, List[PickedGame]]], str]] = None,
        _filter: Optional[Callable[[Tuple[Any, List[PickedGame]]], bool]] = None,
        take: Optional[int] = None,
        custom_suffix: Optional[Callable[[Tuple[Any, List[PickedGame]]], str]] = None,
        progress_indicator: Optional[
            Callable[[Tuple[Any, List[PickedGame]]], Tuple[float, float]]
        ] = None,
        priority_determinator: Optional[
            Callable[[ExcelGame, ExcelGame], ExcelGame]
        ] = None,
        should_rank: bool = True,
    ):
        self.grouping = grouping or self.__default_grouping
        self.sort = sort or self.__default_sort
        self.reverse = reverse
        self.subgroupings = subgroupings or []
        self.get_group_name = get_group_name or self.__default_group_name
        self.filter = _filter or self.__default_filter
        self.take = take
        self.custom_suffix = custom_suffix or self.__default_suffix
        self.progress_indicator = progress_indicator
        self.priority_determinator = (
            priority_determinator or self.__default_priority_determinator
        )
        self.should_rank = should_rank

        self._selection_sort = None
        self._reverse_selection_sort = False

    def __default_grouping(self, g: ExcelGame):
        return g.platform

    def __default_sort(self, kvp: Tuple[Any, List[PickedGame]]):
        return str.casefold(str(kvp[0]))

    def __default_filter(self, _):
        return True

    def __default_suffix(self, _):
        return ""

    def __default_group_name(self, kvp: Tuple[Any, List[PickedGame]]):
        title = kvp[0]
        num_entries = min(len(kvp[1]), len(kvp[1][: self.take]))

        games = kvp[1]

        if self.take:
            games = sorted(
                games, key=self._selection_sort, reverse=self._reverse_selection_sort
            )

        total_playtime = sum(g.game.estimated_playtime or 0 for g in games[: self.take])

        total_playtime_str = ""

        if total_playtime > 0:
            total_playtime_str = (
                " ["
                + (
                    f"{int(total_playtime):,}"
                    if isinstance(total_playtime, int) or total_playtime.is_integer()
                    else (
                        f"{total_playtime:,.2f}"
                        if total_playtime >= 1
                        else f"{int(total_playtime*60)}"
                    )
                )
                + f"{'hr' if total_playtime >= 1 else 'min'}]"
            )

        progress = ""

        if self.progress_indicator is not None:
            prog = self.progress_indicator(kvp)
            progress = f" - {prog[0] / prog[1]:.0%} complete ({prog[0]}/{prog[1]})"

        return f"{title} ({num_entries:,}){total_playtime_str}{progress}{self.custom_suffix(kvp)}"

    def __default_priority_determinator(
        self, g1: ExcelGame, g2: ExcelGame
    ) -> ExcelGame:
        if (g1.combined_rating or 0) > (g2.combined_rating or 0):
            return g1
        if (g1.combined_rating or 0) == (
            g2.combined_rating or 0
        ) and g1.normal_title > g2.normal_title:
            return g1

        return g2

    def __get_grouping(
        self, games: List[ExcelGame], by: Callable[[ExcelGame], Any]
    ) -> Dict[Any, List[PickedGame]]:
        by_value: Dict[Any, List[ExcelGame]] = {}
        highest_by_value: Dict[Any, ExcelGame] = {}

        for game in games:
            group_key = by(game)
            if by_value.get(group_key):
                by_value[group_key].append(game)

                highest_by_value[group_key] = self.priority_determinator(
                    game, highest_by_value[group_key]
                )
            else:
                by_value[group_key] = [game]
                highest_by_value[group_key] = game

        return {
            key: [
                PickedGame(
                    game,
                    high_priority=self.should_rank
                    and (game.combined_rating or 0) >= 0.8,
                    highest_priority=self.should_rank and highest_by_value[key] == game,
                )
                for game in _games
            ]
            for key, _games in by_value.items()
        }

    def get_groups(self, games: List[ExcelGame], _sorted: bool = True) -> GameGroups:
        grouping = self.__get_grouping(games, by=self.grouping)

        return GameGroups(
            OrderedDict(
                list(
                    filter(
                        self.filter,
                        (
                            sorted(
                                grouping.items(), key=self.sort, reverse=self.reverse
                            )
                            if _sorted
                            else grouping.items()
                        ),
                    )
                )
            )
        )

    def set_selection_sort(
        self, sort: Optional[Callable[[PickedGame], Any]], reverse: bool
    ):
        self._selection_sort = sort
        self._reverse_selection_sort = reverse
