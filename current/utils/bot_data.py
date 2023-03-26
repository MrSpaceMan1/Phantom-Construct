"""Class that allows for easy read/write of bot data such as configs, lists of users, etc."""
import json, dotenv
from typing import Optional, TextIO

env = dotenv.dotenv_values()


class BotData:
    def __init__(self, bot):
        self.__data = {}
        self.bot = bot

    def __call__(self) -> dict:
        return self.__data

    def __setitem__(self, key, value) -> None:
        self.__data[key] = value
        json_string = json.dumps(self.__data, indent=4)

        with open(env["BOT_DATA"], "w") as bot_data_file:
            bot_data_file.write(json_string)

    def __getitem__(self, key) -> Optional[str or int or list[int] or list[str]]:
        return self.__data.get(key)

    def load(self, file: TextIO):
        json_dict = json.loads(file.read())
        self.__data = json_dict

    def __repr__(self) -> str:
        return self.__data.__str__()
