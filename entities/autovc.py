from typing import TYPE_CHECKING

import discord as d
from discord import VoiceChannel, Member, Interaction, HTTPException, Guild
import data_classes

if TYPE_CHECKING:
    from bot.my_bot import MyBot
    from data_classes.dynamic_voicechat_data import DynamicVoicechatRequests
    from bot.bot_data import BotState


class AutoVC:
    GENERAL_NAME: str = "Hangout"

    def __init__(self, bot: "MyBot", channel: VoiceChannel, member: Member):
        self.bot: "MyBot" = bot
        self.channel: VoiceChannel = channel
        self.owner: Member = member
        self.locked: bool = False
        self.requests: list["DynamicVoicechatRequests"] = []
        self.request_join_channel_id: int = None

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
            trigger_channel_id = state.autovc_config.trigger_channel_id
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
    async def __handle_request_channel(cls, interaction: Interaction, state: "BotState", bot: "MyBot"):
        voice_channel = interaction.user.voice.channel

        autovc_data = state.autovc_list.get(str(voice_channel.id), None)

        if autovc_data.locked:
            request_channel = await bot.get_or_fetch_channel(autovc_data.request_join_channel_id)
            if request_channel:
                await request_channel.delete()
        else:
            ...

    @classmethod
    def __create_overwrites(cls, interaction: Interaction, state: "BotState") -> dict[d.Member | d.Role, d.PermissionOverwrite]:
        voice_channel = interaction.user.voice.channel
        current_occupants = voice_channel.members
        channel_permissions = voice_channel.overwrites

        autovc_data = state.autovc_list.get(str(voice_channel.id), None)

        base_role = None
        if base_role_id := state.autovc_config.base_role_id:
            base_role = interaction.guild.get_role(base_role_id)

        default_role = interaction.guild.default_role
        deny_connect = d.PermissionOverwrite(connect=False)
        allow_connect = d.PermissionOverwrite(connect=True)
        unset_connect = d.PermissionOverwrite(connect=None)
        if not autovc_data.locked:
            permissions_overwrites: dict[d.Member | d.Role, d.PermissionOverwrite] = {
                default_role: deny_connect,
            }
            for occupant in current_occupants:
                permissions_overwrites[occupant] = allow_connect
            if base_role:
                permissions_overwrites.update({base_role: deny_connect})
            channel_permissions.update(permissions_overwrites)
        else:
            permissions_overwrites = {
                default_role: unset_connect,
            }

            for key in channel_permissions:
                if isinstance(key, d.Member):
                    permissions_overwrites[key] = unset_connect

            if base_role:
                permissions_overwrites.update({base_role: unset_connect})

        return permissions_overwrites

    @classmethod
    async def lock(cls, interaction: Interaction, bot: "MyBot"):

        owner = interaction.guild.get_member(interaction.user.id)
        guild = interaction.guild
        voice_channel = owner.voice.channel

        if voice_channel is None:
            return await interaction.respond("You are not in a voice channel", ephemeral=True)

        with bot.data.access_write() as write_state:
            autovc_data = write_state.autovc_list.get(str(voice_channel.id), None)
            return_msg = "Channel has been unlocked"

            if autovc_data is None:
                return await interaction.respond("You are not in a dynamic voice channel", ephemeral=True)

            if owner.id != autovc_data.owner_id:
                return await interaction.respond("You are not the owner of dynamic voice channel", ephemeral=True)

            permission_overwrites = cls.__create_overwrites(interaction, write_state)

            try:
                await voice_channel.edit(overwrites=permission_overwrites)

                request_channel = await guild.create_voice_channel(
                    "Request to join ⬇",
                    position=voice_channel.position,
                    category=voice_channel.category
                )
                autovc_data.locked = not autovc_data.locked
                autovc_data.request_join_channel_id = request_channel.id
            except d.HTTPException:
                return await interaction.respond("An error occurred. Try again later.", ephemeral=True)

            return await interaction.respond(return_msg, ephemeral=True)

    @classmethod
    async def rename(cls, name: str, *, interaction: Interaction, bot: "MyBot"):
        await interaction.response.defer(ephemeral=True)
        owner: d.Member = interaction.guild.get_member(interaction.user.id)

        if owner is None:
            return await interaction.respond("Access violation.")

        voice_channel = owner.voice.channel

        if voice_channel is None:
            return await interaction.respond("You are not in a voice channel", ephemeral=True)

        with bot.data.access_write() as write_state:
            voice_channel_id = str(voice_channel.id)
            vc_data = write_state.autovc_list.get(voice_channel_id)

            if not vc_data:
                return await interaction.respond("You are not in a dynamic voice channel", ephemeral=True)

            try:
                await voice_channel.edit(name=name)
            except HTTPException:
                return await interaction.respond("Discord error occurred. Sorry.")
            vc_data.name = name
            return await interaction.respond("Renamed the channel", ephemeral=True)