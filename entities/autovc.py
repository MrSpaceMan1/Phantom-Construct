import discord as d
from discord import VoiceChannel
from data_classes import DynamicVoicechatData


class AutoVC:
    GENERAL_NAME = "General auto VC"
    PASSWORD = "password"
    MAX = "max"

    def __init__(self, bot, name, channel):
        self.bot = bot
        self.name = name
        self.channel = channel

        with self.bot.data.access_write() as write_state:
            write_state.autovc_list[str(self.channel.id)] = DynamicVoicechatData(self)

    @classmethod
    async def create(cls, bot, guild, category, presence=None):
        name = AutoVC.GENERAL_NAME
        try:
            if presence.type == d.ActivityType.playing:
                name = presence.name
        except AttributeError:
            pass  # fuck you python

        with bot.data.access() as state:
            trigger_channel_id = state.autovc_channel
            trigger_channel = await bot.get_or_fetch_channel(trigger_channel_id)
            if type(trigger_channel) is not VoiceChannel:
                raise Exception("Trigger channel not a voice channel")
            position = trigger_channel.position + 1
            channel = await guild.create_voice_channel(name, category=category, position=position)

        return cls(bot, name, channel)
