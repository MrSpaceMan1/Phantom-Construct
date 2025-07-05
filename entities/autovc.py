import discord as d
from discord import VoiceChannel
import data_classes


class AutoVC:
    GENERAL_NAME = "Hangout"

    def __init__(self, bot, channel, member):
        self.bot = bot
        self.channel = channel
        self.owner = member
        self.locked = False
        self.requests = []

        with self.bot.data.access_write() as write_state:
            write_state.autovc_list[str(self.channel.id)] = data_classes.DynamicVoicechatData.from_dynamic_voice_chat(self)

    @classmethod
    async def create(cls, bot, member):
        name_ends_with_s = member.display_name.endswith("s")
        apostrophe = "'" if name_ends_with_s else "'s"
        name = f"{member.display_name}{apostrophe} {AutoVC.GENERAL_NAME}"
        try:
            if member.activity.type == d.ActivityType.playing:
                name = member.activity.name
        except AttributeError:
            pass  # fuck you python

        with bot.data.access() as state:
            trigger_channel_id = state.autovc_channel
            trigger_channel = await bot.get_or_fetch_channel(trigger_channel_id)
            if type(trigger_channel) is not VoiceChannel:
                raise Exception("Trigger channel not a voice channel")
            position = trigger_channel.position
            channel = await trigger_channel.guild.create_voice_channel(name, category=trigger_channel.category, position=position)

        return cls(bot, channel, member)
