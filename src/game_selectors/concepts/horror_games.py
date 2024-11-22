from excel_game import ExcelGenre
from data_provider import DataProvider
from game_selector import GameSelector


def get_horror_games_selector(data_provider: DataProvider) -> GameSelector:
    validator = data_provider.get_validator()
    titles = data_provider.get_giant_bomb_titles_for_concept("3015-4801").union(
        data_provider.get_moby_games_titles_for_group(4822)
    )

    return GameSelector(
        _filter=lambda game: game.genre == ExcelGenre.SURVIVAL_HORROR
        or any(validator.titles_equal_normalized(game.title, t) for t in titles),
        name="Horror Games",
    )
