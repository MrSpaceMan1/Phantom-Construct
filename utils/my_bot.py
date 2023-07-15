from typing import Optional, Type, TypeVar
import discord as d
from discord.abc import Messageable
from utils import bot_data, warning_system, volatile_storage


class MyBot(d.Bot):
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

    T = TypeVar("T", bound=d.abc.Messageable)

    async def get_or_fetch_channel(self, _id: int) -> Optional[T]:
        """Gets channel from cache or fetches it from discord. Returns Optional[Messageable]"""
        get_res = self.get_channel(_id)
        if get_res is not None:
            return get_res
        fetch_res = await self.fetch_channel(_id)
        return fetch_res

    async def get_or_fetch_message(self, channel_id: int, message_id: int) -> Optional[d.Message]:
        if not all([channel_id, message_id]):
            return None
        msg = self.get_message(message_id)
        if msg:
            return msg

        channel = await self.get_or_fetch_channel(channel_id)
        if not channel:
            return None
        else:
            return await channel.fetch_message(message_id)

    def is_user_a_member(self, user: d.User) -> Optional[d.Member]:
        """Checks if user is a member. Returns discord.Member"""
        return d.utils.find(lambda member: member == user, self.get_all_members())
