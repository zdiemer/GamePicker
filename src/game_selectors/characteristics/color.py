import asyncio
import io
import logging
import logging.config
import os
from typing import List, Optional, Tuple

import aiohttp
import webcolors
from excel_game import ExcelGame, ExcelRegion
from game_match import DataSource
from PIL import Image, UnidentifiedImageError

from data_provider import DataProvider
from game_grouping import GameGrouping
from game_selector import GameSelector
from output_parser import OutputParser
from picker_enums import PickerMode

country_mapping = {
    ExcelRegion.ITALY: ["IT", "EU"],
    ExcelRegion.EUROPE: ["IT", "GB", "SW", "ES", "DE", "EU"],
    ExcelRegion.SWEDEN: ["SW", "EU"],
    ExcelRegion.BRAZIL: ["BR"],
    ExcelRegion.JAPAN: ["JP"],
    ExcelRegion.AUSTRALIA: ["AU"],
    ExcelRegion.NORTH_AMERICA: ["US", "NOREGION", "CA"],
    ExcelRegion.SPAIN: ["ES", "EU"],
    ExcelRegion.GERMANY: ["DE", "EU"],
    ExcelRegion.ASIA: ["JP"],
    ExcelRegion.KOREA: ["JP"],
    ExcelRegion.CHINA: ["JP"],
    ExcelRegion.TAIWAN: ["JP"],
    ExcelRegion.FRANCE: ["EU"],
}

format_mapping = {
    ExcelRegion.ASIA: "NTSC-J",
    ExcelRegion.JAPAN: "NTSC-J",
    ExcelRegion.NORTH_AMERICA: "NTSC",
    ExcelRegion.EUROPE: "PAL",
    ExcelRegion.AUSTRALIA: "PAL",
    ExcelRegion.ITALY: "PAL",
    ExcelRegion.SWEDEN: "PAL",
    ExcelRegion.BRAZIL: "NTSC",
    ExcelRegion.SPAIN: "PAL",
    ExcelRegion.GERMANY: "PAL",
    ExcelRegion.FRANCE: "PAL",
    ExcelRegion.KOREA: "NTSC-J",
    ExcelRegion.CHINA: "NTSC-J",
    ExcelRegion.TAIWAN: "NTSC-J",
}


def get_dominant_color(
    pil_img: Image.Image, palette_size: int = 16
) -> Tuple[int, int, int]:
    img = pil_img.copy()
    img.thumbnail((100, 100))
    paletted = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=palette_size)

    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    dominant_color = palette[palette_index * 3 : palette_index * 3 + 3]

    return dominant_color


def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors._definitions._CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]


def get_color_name(rgb_tuple):
    try:
        hex_value = webcolors.rgb_to_hex(rgb_tuple)
        return webcolors.hex_to_name(hex_value)
    except ValueError:
        return closest_color(rgb_tuple)


def get_color_selector(data_provider: DataProvider) -> GameSelector:
    color_output = OutputParser.get_source_output(DataSource.THE_COVER_PROJECT)

    logging.basicConfig(level=logging.WARN)

    async def get_game_dominant_color(game: ExcelGame) -> Optional[str]:
        if game.hash_id in color_output:
            for cover in color_output[game.hash_id].match_info["covers"]:
                if (
                    cover["country"] in country_mapping[game.release_region]
                    and cover["format"] == format_mapping[game.release_region]
                    and not cover["custom_cover"]
                ):
                    folder_path = "caches\\images"
                    file_name = cover["image_url"].split("/")[-1]
                    relative_path = os.path.join(folder_path, file_name)
                    cover_bytes = None

                    if os.path.isfile(relative_path):
                        with open(relative_path, "rb") as f:
                            cover_bytes = io.BytesIO(f.read())

                    if cover_bytes is None:
                        async with aiohttp.ClientSession() as session:
                            print(f"Requesting {cover['image_url']}")
                            async with session.get(cover["image_url"]) as res:
                                cover_bytes = io.BytesIO(await res.content.read())
                                with open(relative_path, "wb") as f:
                                    f.write(cover_bytes.getbuffer())
                                cover_bytes.seek(0)

                    try:
                        with Image.open(cover_bytes) as image:
                            rgb_tuple = get_dominant_color(image)
                            return get_color_name(rgb_tuple)
                    except (UnidentifiedImageError, ValueError):
                        return None
        return None

    def get_dominant_colors(games: List[ExcelGame]) -> List[ExcelGame]:
        output: List[ExcelGame] = []

        for game in games:
            color = asyncio.run(get_game_dominant_color(game))

            if color is not None:
                output.append(game.get_copy_with_metadata(color))

        return output

    return GameSelector(
        get_dominant_colors,
        _filter=lambda game: game.group_metadata is not None,
        name="Color",
        run_on_modes=set([PickerMode.ALL]),
        include_in_picks=False,
        skip_unless_specified=True,
        no_force=True,
        grouping=GameGrouping(
            lambda g: g.group_metadata,
            should_rank=False,
        ),
    )
