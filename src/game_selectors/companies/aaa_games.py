from game_match import DataSource
from game_selector import GameSelector
from output_parser import OutputParser

AAA_GAMES = GameSelector(
    lambda games: OutputParser.get_source_output_filtered(
        games,
        DataSource.VG_CHARTZ,
        lambda gm: (gm.match_info.get("total_shipped") or 0) >= 1_000_000,
    ),
    name="AAA Games",
    sort=lambda g: g.game.group_metadata["total_shipped"],
    reverse_sort=True,
    custom_suffix=lambda g: f' - {int(g.group_metadata["total_shipped"]):,} units',
)
