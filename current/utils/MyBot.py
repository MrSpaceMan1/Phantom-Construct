import discord
from discord.abc import Messageable
from . import BotData
from typing import Optional


class MyBot(discord.Bot):

    def __init__(self, *args, **options):
        super().__init__(*args, **options)
        self.__data: BotData.BotData = BotData.BotData(self)

    @property
    def data(self):
        if not self.__data:
            return None
        return self.__data

    async def get_or_fetch_channel(self, id: int) -> Optional[Messageable]:
        get_res = self.get_channel(id)
        if get_res is not None:
            return get_res
        fetch_res = await self.fetch_channel(id)
        return fetch_res