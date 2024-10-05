from typing import Iterator
import discord as d
from discord.ext import commands
from autovc import AutoVC
from data_classes import DynamicVoicechatData
from utils.iterable_methods import find
from bot.my_bot import MyBot


class DynamicVoiceChatCog(d.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot
        self.trigger_channel: int = None

    permissions = d.Permissions()
    permissions.connect = True
    vc = d.SlashCommandGroup(
        "auto-vc",
        "Group of commands to set dynamic voice channels",
        default_member_permissions=permissions
    )

    @vc.command(name="set-trigger-channel")
    async def set_trigger_channel(
            self,
            ctx: d.ApplicationContext,
            channel: d.Option(d.VoiceChannel, description="Channel to set")
    ):
        """Set the channel that will trigger channel creation"""
        with self.bot.data.access_write() as write_state:
            write_state.autovc_channel = int(channel.id)
        await ctx.respond("Channel set", ephemeral=True)

    @vc.command(name="rename", description="Rename channel you are in")
    async def rename(
            self,
            ctx: d.ApplicationContext,
            name: d.Option(str, description="Overrides current channel name")
    ):
        member: d.Member = ctx.guild.get_member(ctx.user.id)
        if member is None:
            return

        voice_channel = member.voice.channel

        if voice_channel is None:
            await ctx.respond("You are not in a voice channel", ephemeral=True)
            return

        with self.bot.data.access() as state:
            autovc_list: dict[int, DynamicVoicechatData] = state.autovc_list
        if str(voice_channel.id) not in autovc_list.keys():
            await ctx.respond("You are not in a dynamic voice channel", ephemeral=True)
            return

        await voice_channel.edit(name=name)
        await ctx.respond("Renamed the channel", ephemeral=True)

    @vc.command()
    async def lock(
            self,
            ctx: d.ApplicationContext,
            password: d.Option(str, description="Password for the channel; If empty will remove the lock", default="", required=False)):
        """Set password to lock channel. Remember it, because you won't be reminded of it"""

        member: d.Member = ctx.guild.get_member(ctx.user.id)
        if member is None:
            return
        voice_channel = member.voice.channel

        if voice_channel is None:
            await ctx.respond("You are not in a voice channel", ephemeral=True)
            return

        with self.bot.data.access() as state:
            autovc_list: dict[str, DynamicVoicechatData] = state.autovc_list
        autovc = autovc_list.get(str(voice_channel.id))
        if not autovc:
            await ctx.respond("You are not in a dynamic voice channel", ephemeral=True)
            return

        overwrite = d.PermissionOverwrite()
        if password == "":
            overwrite.connect = None
            for member in voice_channel.overwrites.keys():
                await voice_channel.set_permissions(target=member, overwrite=overwrite)

            return await ctx.respond("Lock removed", ephemeral=True)

        overwrite.connect = False
        roles = await ctx.guild.fetch_roles()
        everyone = find(roles, lambda x: x.name == "@everyone")
        await voice_channel.set_permissions(target=roles[everyone], overwrite=overwrite)

        overwrite_keys: Iterator[d.Role | d.Member] = iter(voice_channel.overwrites.keys())

        overwrite.connect = None
        for key in overwrite_keys:
            if type(key) == d.Role:
                continue

            if find(voice_channel.members, lambda x: x.id == key.id) == -1:
                await voice_channel.set_permissions(target=key, overwrite=overwrite)

        members: list[d.Member] = voice_channel.members

        overwrite.connect = True
        for member in members:
            await voice_channel.set_permissions(target=member, overwrite=overwrite)

        autovc.password = password
        with self.bot.data.access_write() as write_state:
            write_state.autovc_list[str(voice_channel.id)] = autovc

        await ctx.respond("Password set", ephemeral=True)

    @vc.command()
    async def password(
            self,
            ctx: d.ApplicationContext,
            channel: d.Option(d.VoiceChannel, description="Channel you want access to"),
            password: d.Option(str, description="Password for the chosen channel")
    ):
        with self.bot.data.access() as state:
            autovc_list = state.autovc_list
        autovc = autovc_list.get(str(channel.id))
        channel: d.VoiceChannel

        if not autovc:
            return await ctx.respond("Provided channel isn't dynamic", ephemeral=True)

        if autovc.password == "":
            return await ctx.respond("This channel isn't locked", ephemeral=True)

        if autovc.password != password:
            return await ctx.respond("Wrong password", ephemeral=True)

        member: d.Member = ctx.guild.get_member(ctx.user.id) or (await ctx.guild.fetch_member(ctx.user.id))

        overwrite = d.PermissionOverwrite()
        overwrite.connect = True

        await channel.set_permissions(target=member, overwrite=overwrite)
        await ctx.respond("Access granted", ephemeral=True)

    @commands.Cog.listener("on_voice_state_update")
    async def detect_trigger_channel(self, member: d.Member, _, new_state: d.VoiceState):
        if not self.trigger_channel:
            with self.bot.data.access() as state:
                self.trigger_channel = state.autovc_channel

        channel: d.VoiceChannel = new_state.channel
        if channel is None:
            return
        if self.trigger_channel is None:
            return
        if channel.id != self.trigger_channel:
            return

        category = channel.category
        presence = member.activity
        new_channel = await AutoVC.create(self.bot, guild=channel.guild, category=category, presence=presence)

        await member.move_to(new_channel.channel)

    @commands.Cog.listener("on_voice_state_update")
    async def detect_empty_channels(self, member, old_state: d.VoiceState, _):
        channel: d.VoiceChannel = old_state.channel
        with self.bot.data.access_write() as state:
            autovc_list = state.autovc_list

            if channel is None:
                return
            if not autovc_list:
                return
            if autovc_list.get(str(channel.id)) is None:
                return
            if len(channel.members) != 0:
                return

            if autovc_list.get(str(channel.id)):
                del state.autovc_list[str(channel.id)]
                await channel.delete()


def setup(bot: MyBot):
    bot.add_cog(DynamicVoiceChatCog(bot))
