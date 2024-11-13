from typing import Optional
from bot.my_bot import MyBot
import discord


class AutoVC:
    GENERAL_NAME = "General auto VC"
    PASSWORD = "password"

    def __init__(self, bot: MyBot, name: str, channel: discord.VoiceChannel, member: discord.Member):
        self.bot: MyBot = ...
        self.name: str = ...
        self.channel: discord.VoiceChannel = ...
        self.password: str = ...
        self.owner: discord.Member = ...

    @classmethod
    async def create(
            cls,
            bot: MyBot,
            member: discord.Member,
    ) -> AutoVC:...