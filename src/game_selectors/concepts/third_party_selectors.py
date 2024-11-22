from typing import List, Optional

from data_provider import DataProvider
from game_selector import GameSelector


def get_third_party_selector(
    data_provider: DataProvider,
    name: str,
    giant_bomb_concept_guids: Optional[List[str]] = None,
    moby_games_group_ids: Optional[List[int]] = None,
):
    validator = data_provider.get_validator()
    titles = set()

    for concept_guid in giant_bomb_concept_guids or []:
        titles = titles.union(
            data_provider.get_giant_bomb_titles_for_concept(concept_guid)
        )

    for group_id in moby_games_group_ids or []:
        titles = titles.union(data_provider.get_moby_games_titles_for_group(group_id))

    return GameSelector(
        _filter=lambda g: any(
            validator.titles_equal_normalized(g.title, t) for t in titles
        ),
        name=name,
    )
