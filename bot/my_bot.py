from typing import Optional, TypeVar, Self, Union

import discord
import discord as d
from discord import Thread, Message, Guild, User, Forbidden, Member
from discord.abc import GuildChannel, PrivateChannel

from bot import warning_system, bot_data, volatile_storage


class MyBot(d.Bot):
    """Custom bot"""
    instance: "MyBot" = None

    def __init__(self, *args, **options):
        super().__init__(*args, assume_unsync_clock=True, **options)
        self.__data: "bot_data.BotStateManager" = bot_data.BotStateManager()
        self.__warnings_system: "warning_system.WarningSystem" = warning_system.WarningSystem(self)
        self.__session: "volatile_storage.VolatileStorage" = volatile_storage.VolatileStorage()
        MyBot.instance = self

    @property
    def data(self) -> "bot_data.BotStateManager":
        """Returns BotData object"""
        return self.__data

    @property
    def warnings(self) -> "warning_system.WarningSystem":
        """Returns WarningSystem object"""
        return self.__warnings_system

    @property
    def session(self) -> "volatile_storage.VolatileStorage":
        """Returns session's VolatileStorage object """
        return self.__session

    @classmethod
    def get_instance(cls) -> "MyBot":
        """Returns instance of MyBot class"""
        return MyBot.instance

    async def get_or_fetch_channel(self, _id: int) -> Optional[Union[GuildChannel, PrivateChannel, Thread]]:
        """Gets channel from cache or fetches it from discord. Returns Optional[GuildChannel]"""
        get_res = self.get_channel(_id)
        if get_res is not None:
            return get_res
        fetch_res = await self.fetch_channel(_id)
        return fetch_res

    async def get_or_fetch_message(self, channel_id: int, message_id: int) -> Optional[Message]:
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

    async def is_user_a_member(self, guild: Guild, user: User) -> Optional[Member]:
        """Checks if user is a member. Returns discord.Member"""
        member = guild.get_member(user.id)
        if member:
            return member
        try:
           member = await guild.fetch_member(user.id)
           return member
        except Forbidden:
            return None
