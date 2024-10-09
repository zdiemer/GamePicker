import datetime
import os
import pickle
import pytz

from typing import Any


class ExcelBackedCache:
    __BASE_DROPBOX_FOLDER = "C:\\Users\\zachd\\Dropbox\\Video Game Lists"
    __EXCEL_SHEET_NAME = "Games Master List - Final.xlsx"

    def __get_excel_file_name(self) -> str:
        return f"{self.__BASE_DROPBOX_FOLDER}\\{self.__EXCEL_SHEET_NAME}"

    def load(self, cache_file_name: str) -> Any:
        if not os.path.exists(cache_file_name):
            return None

        with open(cache_file_name, "rb") as inp:
            (data, cache_time) = pickle.load(inp)

            modify_timestamp_pt = os.path.getmtime(self.__get_excel_file_name())
            modify_time_utc = datetime.datetime.fromtimestamp(
                modify_timestamp_pt, tz=pytz.timezone("America/Los_Angeles")
            ).astimezone(datetime.UTC)

            if modify_time_utc <= cache_time:
                return data

            return None

    def write(self, cache_file_name: str, data: Any):
        with open(cache_file_name, "wb") as outp:
            pickle.dump(
                (
                    data,
                    datetime.datetime.now(datetime.UTC),
                ),
                outp,
                pickle.HIGHEST_PROTOCOL,
            )
