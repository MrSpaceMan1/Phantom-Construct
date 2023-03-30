import json
from typing import Optional, TextIO, Union, Any
import dotenv

env = dotenv.dotenv_values()


class BotData:
    """Class that allows for easy read/write of bot data such as configs, lists of users, etc."""
    def __init__(self, bot):
        """Creates BotData object"""
        self.__data = {}
        self.bot = bot

    def __call__(self) -> dict:
        """Returns data dictionary"""
        return self.__data

    def __setitem__(self, key, value) -> None:
        """Sets value for a key in data dictionary"""
        self.__data[key] = value
        json_string = json.dumps(self.__data, indent=4)

        with open(env["BOT_DATA"], "w", encoding="utf-8") as bot_data_file:
            bot_data_file.write(json_string)

    def __getitem__(self, key) -> Optional[Union[str, int, list[str], list[int], dict[Any, Any]]]:
        """Retrieves value of given key. Returns Optional[Union[str, int, list[str], list[int]]]"""
        return self.__data.get(key)

    def load(self, file: TextIO):
        """Loads data from a file interface"""
        json_dict = json.loads(file.read())
        self.__data = json_dict

    def __repr__(self) -> str:
        """Implementation of __repr__"""
        return self.__data.__str__()
