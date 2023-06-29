from typing import Optional
import discord
from discord.abc import Messageable
from . import bot_data, warning_system, volatile_storage


class MyBot(discord.Bot):
    """Custom bot"""
    instance = None

    def __init__(self, *args, **options):
        super().__init__(*args, **options)
        self.__data: bot_data.BotData = bot_data.BotData(self)
        self.__warnings_system: warning_system.WarningSystem = warning_system.WarningSystem(self)
        self.__session: volatile_storage.VolatileStorage = volatile_storage.VolatileStorage(self)
        MyBot.instance = self

    @property
    def data(self):
        """Returns BotData object"""
        return self.__data

    @property
    def warnings(self):
        """Returns WarningSystem object"""
        return self.__warnings_system

    @property
    def session(self):
        """Returns session's VolatileStorage object """
        return self.__session

    @staticmethod
    def get_instance():
        """Returns instance of MyBot class"""
        return MyBot.instance

    async def get_or_fetch_channel(self, _id: int) -> Optional[Messageable]:
        """Gets channel from cache or fetches it from discord. Returns Optional[Messageable]"""
        get_res = self.get_channel(_id)
        if get_res is not None:
            return get_res
        fetch_res = await self.fetch_channel(_id)
        return fetch_res

    def is_user_a_member(self, user: discord.User) -> Optional[discord.Member]:
        """Checks if user is a member. Returns discord.Member"""
        return discord.utils.find(lambda member: member == user, self.get_all_members())
