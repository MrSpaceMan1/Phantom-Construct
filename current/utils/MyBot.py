import discord
from discord.abc import Messageable
from . import BotData, WarningSystem, VolatileStorage
from typing import Optional


class MyBot(discord.Bot):

    def __init__(self, *args, **options):
        super().__init__(*args, **options)
        self.__data: BotData.BotData = BotData.BotData(self)
        self.__warnings_system: WarningSystem.WarningSystem = WarningSystem.WarningSystem(self)
        self.__session: VolatileStorage.VolatileStorage = VolatileStorage.VolatileStorage(self)

    @property
    def data(self):
        if not self.__data:
            return None
        return self.__data

    @property
    def warnings(self):
        if not self.__warnings_system:
            return None
        return self.__warnings_system

    @property
    def session(self):
        if not self.__session:
            return None
        return self.__session

    async def get_or_fetch_channel(self, id: int) -> Optional[Messageable]:
        get_res = self.get_channel(id)
        if get_res is not None:
            return get_res
        fetch_res = await self.fetch_channel(id)
        return fetch_res

    def is_user_a_member(self, user: discord.User):
        return discord.utils.find(lambda member: member == user, self.get_all_members())

