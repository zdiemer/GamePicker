from typing import List, Set
import re

from spellchecker import SpellChecker

from excel_game import ExcelGame
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def misspellings(games: List[ExcelGame]) -> List[ExcelGame]:
    misspelled = []
    checker = SpellChecker()
    checker.word_frequency.load_text_file("dictionary.txt")

    def get_words(t: str) -> Set[str]:
        words = t.split()
        output_words = set()

        for word in words:
            word = re.sub(r"[^A-Za-z0-9\s]", "", word).strip()
            compound = re.findall(r"[A-Z][^A-Z]*", word)

            if any(compound):
                if not any(checker.unknown([word])):
                    continue
                output_words = output_words.union(set(compound))
                continue

            output_words.add(word)

        return output_words.difference(set([""]))

    all_misspelled_words = set([])

    for game in games:
        title_words = get_words(game.title)
        misspelled_words = checker.unknown(title_words)
        all_misspelled_words = all_misspelled_words.union(set(misspelled_words))

        for word in misspelled_words:
            if checker.correction(word) is not None:
                print(f"Found a misspelled word {word} for {game.full_name}")
                misspelled.append(game)
                break

    return misspelled


MISSPELLINGS = GameSelector(
    misspellings,
    run_on_modes=set([PickerMode.ALL]),
    include_in_picks=False,
    include_platform=False,
    grouping=GameGrouping(should_rank=False),
)
