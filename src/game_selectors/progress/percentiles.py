from excel_game import ExcelGame
from data_provider import DataProvider, Percentile
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def group_by_percentile(game: ExcelGame, data_provider: DataProvider) -> str:
    p1 = data_provider.get_percentile_ranking(Percentile.P1)
    p5 = data_provider.get_percentile_ranking(Percentile.P5)
    p10 = data_provider.get_percentile_ranking(Percentile.P10)
    p25 = data_provider.get_percentile_ranking(Percentile.P25)
    med = data_provider.get_percentile_ranking(Percentile.MED)
    p75 = data_provider.get_percentile_ranking(Percentile.P75)
    p90 = data_provider.get_percentile_ranking(Percentile.P90)
    p95 = data_provider.get_percentile_ranking(Percentile.P95)
    p99 = data_provider.get_percentile_ranking(Percentile.P99)

    if game.combined_rating < p1:
        return f"1st (<{p1:.02%})"

    if game.combined_rating < p5:
        return f"1-5th ({p1:.02%}-{p5:.02%})"

    if game.combined_rating < p10:
        return f"5-10th ({p5:.02%}-{p10:.02%})"

    if game.combined_rating < p25:
        return f"10-25th ({p10:.02%}-{p25:.02%})"

    if game.combined_rating < med:
        return f"25-49th ({p25:.02%}-{med:.02%})"

    if game.combined_rating < p75:
        return f"50-74th ({med:.02%}-{p75:.02%})"

    if game.combined_rating < p90:
        return f"75-89th ({p75:.02%}-{p90:.02%})"

    if game.combined_rating < p95:
        return f"90-94th ({p90:.02%}-{p95:.02%})"

    if game.combined_rating < p99:
        return f"95-98th ({p95:.02%}-{p99:.02%})"

    return f"99th (>={p99:.02%})"


def get_percentiles_selector(data_provider: DataProvider) -> GameSelector:
    return GameSelector(
        name="Percentiles",
        grouping=GameGrouping(
            lambda g: group_by_percentile(g, data_provider),
            reverse=True,
            sort=lambda kvp: max(g.game.combined_rating for g in kvp[1]),
        ),
        custom_suffix=lambda g: f" - {g.combined_rating:.0%}",
        sort=lambda g: g.game.combined_rating,
        reverse_sort=True,
        run_on_modes=set([PickerMode.ALL]),
    )
