from game_selector import GameSelector


def is_palindrome(text: str) -> bool:
    # Remove all non-alphanumeric characters and convert to lowercase
    cleaned = "".join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]


PALINDROME_GAMES = GameSelector(
    _filter=lambda g: is_palindrome(g.title),
    name="Palindromes",
)
