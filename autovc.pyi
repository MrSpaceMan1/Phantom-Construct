from typing import Optional

from my_bot import MyBot
import discord


class AutoVC:
    GENERAL_NAME = "General auto VC"
    PASSWORD = "password"
    MAX = "max"
    def __init__(self, bot: MyBot, name: str, channel: discord.VoiceChannel):
        self.bot: MyBot = ...
        self.name: str = ...
        self.channel: discord.VoiceChannel = ...

    @classmethod
    async def create(
            cls,
            bot: MyBot,
            guild: discord.Guild,
            category: discord.CategoryChannel,
            presence: Optional[discord.Activity] = None
    ) -> AutoVC:...