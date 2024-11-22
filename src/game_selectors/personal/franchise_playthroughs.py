from typing import List, Optional, Tuple

from excel_game import ExcelGame

from data_provider import DataProvider
from excel_filter import ExcelFilter
from game_grouping import GameGrouping
from game_selector import GameSelector
from picker_enums import PickerMode


def franchise_playthroughs(
    data_provider: DataProvider, mode: PickerMode
) -> List[ExcelGame]:
    by_franchise = GameGrouping(lambda g: g.franchise).get_groups(
        list(
            filter(
                lambda g: g.franchise is not None
                and ExcelFilter.included_in_mode(g, mode)
                and ExcelFilter.is_not_low_priority(g)
                and ExcelFilter.is_playable(g)
                and ExcelFilter.is_playable_by_language(g)
                and ExcelFilter.is_unplayed(g)
                and ExcelFilter.is_released(g),
                data_provider.get_games(),
            )
        ),
    )

    by_franchise_played = GameGrouping(lambda g: g.franchise).get_groups(
        list(
            filter(
                lambda g: g.franchise is not None,
                data_provider.get_played_games(),
            )
        ),
    )

    next_up = []

    for franchise in by_franchise_played.keys():
        if franchise in by_franchise:
            next_up.extend(g.game for g in by_franchise[franchise])

    return next_up


def get_franchise_playthroughs_selector(
    data_provider: DataProvider,
    mode: PickerMode,
    franchises: Optional[Tuple[str]] = None,
    name: str = "Franchise Playthroughs",
):
    return GameSelector(
        lambda _: franchise_playthroughs(data_provider, mode),
        grouping=GameGrouping(
            lambda g: g.franchise,
            progress_indicator=lambda kvp: (
                len(
                    list(
                        filter(
                            lambda g: g.franchise == kvp[0],
                            data_provider.get_played_games(),
                        )
                    )
                ),
                len(
                    list(
                        filter(
                            lambda g: g.franchise == kvp[0],
                            data_provider.get_played_games()
                            + data_provider.get_unplayed_candidates(),
                        )
                    )
                ),
            ),
        ),
        sort=lambda g: g.game.release_date,
        _filter=(
            (lambda g: g.franchise is not None)
            if franchises is None
            else (lambda g: g.franchise in franchises)
        ),
        include_in_picks=False,
        name=name,
    )


FRANCHISE_CONTENDERS = (
    "Final Fantasy",
    "Final Fantasy Tactics",
    "Chocobo",
    "Mana",
    "SaGa",
    "Dragon Quest",
    "Megami Tensei",
    "Red Faction",
    "Castlevania",
    "Kirby",
    "Command & Conquer",
    "The Elder Scrolls",
    "Splinter Cell",
    "Alone in the Dark",
    "Silent Hill",
    "The Darkness",
    "Resident Evil",
    "Turok",
    "The Witcher",
    "Halo",
    "Infamous",
    "Uncharted",
    "Dead Island",
    "Dead Rising",
    "Deus Ex",
    "Metal Gear",
    "King's Field",
    "Armored Core",
    "Shadow Tower",
    "Echo Night",
    "Lost Kingdoms",
    "Otogi",
    "Souls",
    "Yakuza",
    "Ys",
    "Xeno",
    "Far Cry",
    "Metroid",
    "Call of Duty",
    "Ace Attorney",
    "Professor Layton",
    "Advance Wars",
    "Assassin's Creed",
    "Star Ocean",
    "Fire Emblem",
    "Tales",
    "Shining",
    "Phantasy Star",
    "The Legend of Heroes",
    "Suikoden",
    "Breath of Fire",
    "Wild Arms",
    "Arc the Lad",
    "Grandia",
    "Hyperdimension Neptunia",
    "Ar tonelico",
    "Final Fantasy Crystal Chronicles",
    "Atelier",
    "Kingdom Hearts",
    "Lunar",
    "Disgaea",
    "Etrian Odyssey",
    "Ogre Battle",
    "Picross",
    "Genkai Tokki",
    "Parasite Eve",
    "Summon Night",
    "Mario RPG",
    "Mario & Luigi",
    "Paper Mario",
    "Mario",
    "The Legend of Zelda",
    "Sonic the Hedgehog",
    "Pikmin",
    "Mega Man",
    "Mega Man X",
    "Mega Man Zero",
    "Mega Man Battle Network",
    "Mega Man Legends",
    "Pokémon",
    "Pokémon Ranger",
    "Pokémon Mystery Dungeon",
    "Jak and Daxter",
    "Ratchet & Clank",
    "Resistance",
    "Spyro the Dragon",
    "Crash Bandicoot",
    "Sly Cooper",
    "Killzone",
    "Chibi-Robo",
    "Grand Theft Auto",
)
