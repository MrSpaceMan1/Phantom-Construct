from typing import Optional
import discord as d
from utils import MyBot
from utils.constants import *


class AutoVC:
    GENERAL_NAME = "General auto VC"
    PASSWORD = "password"
    MAX = "max"

    def __init__(
            self,
            bot: MyBot,
            name: str,
            channel: d.VoiceChannel,
    ):
        self.bot: MyBot = bot
        self.name = name
        self.channel = channel

        autovc_list = self.bot.data.get_or_default(AUTOVC_LIST, dict())
        autovc_list[str(self.channel.id)] = {
            AutoVC.PASSWORD: "",
            AutoVC.MAX: -1
        }
        self.bot.data[AUTOVC_LIST] = autovc_list

    @classmethod
    async def create(
            cls,
            bot: MyBot,
            guild: d.Guild,
            category: d.CategoryChannel,
            presence: Optional[d.Activity] = None,
    ):
        name = AutoVC.GENERAL_NAME
        try:
            if presence.type == d.ActivityType.playing:
                name = presence.name
        except AttributeError:
            pass  # fuck you python

        trigger_channel_id = bot.data[AUTOVC_CHANNEL]
        trigger_channel: d.VoiceChannel = await bot.get_or_fetch_channel(trigger_channel_id)
        position = trigger_channel.position + 1

        channel = await guild.create_voice_channel(name, category=category, position=position)

        return cls(bot, name, channel)
