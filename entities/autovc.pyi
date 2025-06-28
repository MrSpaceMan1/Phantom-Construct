from bot.my_bot import MyBot
import discord

from data_classes.dynamic_voicechat_data import DynamicVoicechatRequests


class AutoVC:
    GENERAL_NAME = "General auto VC"
    PASSWORD = "password"

    def __init__(self, bot: MyBot, channel: discord.VoiceChannel, member: discord.Member):
        self.bot: MyBot = ...
        self.channel: discord.VoiceChannel = ...
        self.locked: bool = ...
        self.owner: discord.Member = ...
        self.requests: list["DynamicVoicechatRequests"] = ...

    @classmethod
    async def create(
            cls,
            bot: MyBot,
            member: discord.Member,
    ) -> AutoVC:...