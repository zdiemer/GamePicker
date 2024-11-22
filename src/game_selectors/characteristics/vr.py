from game_selector import GameSelector

VR = GameSelector(
    _filter=lambda _g: _g.vr,
    name="VR",
    include_in_picks=False,
)
