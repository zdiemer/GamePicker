from data_provider import DataProvider
from game_selector import GameSelector
from picker_enums import PickerMode


def get_alternate_editions_selector(data_provider: DataProvider) -> GameSelector:
    validator = data_provider.get_validator()
    titles = data_provider.get_moby_games_titles_for_group(16538).union(
        data_provider.get_giant_bomb_titles_for_concept("3015-340")
    )

    return GameSelector(
        _filter=lambda g: g.franchise is not None
        and (
            any(validator.titles_equal_normalized(g.title, t) for t in titles)
            or g.normal_title.endswith(" hd")
            or g.normal_title.endswith(" edition")
            or (
                len(g.normal_title.split()) > 1
                and (
                    g.normal_title.split()[-1].startswith("remast")
                    or g.normal_title.split()[-1].startswith("re-")
                )
            )
        ),
        name="Alternate Editions",
        run_on_modes=set([PickerMode.ALL]),
    )
