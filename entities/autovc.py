from typing import TYPE_CHECKING

import discord as d
from discord import VoiceChannel, Member, Interaction
import data_classes

if TYPE_CHECKING:
    from bot.my_bot import MyBot
    from data_classes.dynamic_voicechat_data import DynamicVoicechatRequests


class AutoVC:
    GENERAL_NAME: str = "Hangout"

    def __init__(self, bot: "MyBot", channel: VoiceChannel, member: Member):
        self.bot: "MyBot" = bot
        self.channel: VoiceChannel = channel
        self.owner: Member = member
        self.locked: bool = False
        self.requests: list["DynamicVoicechatRequests"] = []

        with self.bot.data.access_write() as write_state:
            write_state.autovc_list[str(self.channel.id)] = data_classes.DynamicVoicechatData.from_dynamic_voice_chat(self)

    @classmethod
    async def create(cls, bot: "MyBot", member: Member):
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

        from views.AutoVcControlView import AutoVcControlView
        autovc = cls(bot, channel, member)
        await channel.send("Control panel", view=AutoVcControlView(bot))
        return autovc

    @classmethod
    async def lock(cls, interaction: Interaction, bot: "MyBot"):

        owner = interaction.guild.get_member(interaction.user.id)
        voice_channel = owner.voice.channel

        if voice_channel is None:
            return await interaction.respond("You are not in a voice channel", ephemeral=True)

        with bot.data.access_write() as write_state:
            autovc_data = write_state.autovc_list.get(str(voice_channel.id), None)
            permissions_overwrites = {}
            return_msg = "Channel has been unlocked"

            if autovc_data is None:
                return await interaction.respond("You are not in a dynamic voice channel", ephemeral=True)

            if owner.id != autovc_data.owner_id:
                return await interaction.respond("You are not the owner of dynamic voice channel", ephemeral=True)

            base_role = None
            if base_role_id := write_state.autovc_config.base_role_id:
                base_role = interaction.guild.get_role(base_role_id)

            default_role =  base_role or interaction.guild.default_role
            deny_connect = d.PermissionOverwrite(connect=False)
            allow_connect = d.PermissionOverwrite(connect=True)
            if not autovc_data.locked:
                permissions_overwrites = {
                    default_role: deny_connect,
                    owner: allow_connect
                }
                return_msg = "Channel has been locked"
            try:
                await voice_channel.edit(overwrites=permissions_overwrites)
                autovc_data.locked = not autovc_data.locked
            except d.HTTPException:
                return await interaction.respond("An error occurred. Try again later.", ephemeral=True)

            return await interaction.respond(return_msg, ephemeral=True)