from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def get_longest_playthroughs_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        name="Longest Playthroughs",
        _filter=lambda g: g.date_started is not None and g.date_completed is not None,
        grouping=GameGrouping(
            lambda _: "Longest Playthroughs", should_rank=False, group_size=100
        ),
        include_in_picks=False,
        run_on_modes=set([PickerMode.ALL]),
        games=data_provider.get_completed_games(),
        custom_suffix=lambda g: f" - {(g.date_completed - g.date_started).days:,} days - "
        f"[{g.date_started.strftime('%B %d, %Y')} - {g.date_completed.strftime('%B %d, %Y')}]",
        sort=lambda pg: pg.game.date_completed - pg.game.date_started,
        reverse_sort=True,
    )
