from typing import List, TypeVar
import discord as d
import discord.abc
from discord.ext import commands
from utils import MyBot, find, AutoVC
from utils.constants import *


def list_create(arg):
    if arg is list:
        return arg
    else:
        res = list()
        res.append(arg)
        return res


class DynamicVoiceChatCog(d.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    permissions = d.Permissions()
    permissions.connect = True
    vc = d.SlashCommandGroup(
        "auto-vc",
        "Ground of commands to set dynamic voice channels",
        default_member_permissions=permissions
    )

    @vc.command(name="set-trigger-channel")
    async def set_trigger_channel(
            self,
            ctx: d.ApplicationContext,
            channel: d.Option(d.VoiceChannel, description="Channel to set")
    ):
        """Set the channel that will trigger channel creation"""
        self.bot.data[AUTOVC_CHANNEL] = int(channel.id)
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

        autovc_list = self.bot.data[AUTOVC_LIST]
        if voice_channel.id not in autovc_list:
            await ctx.respond("You are not in a dynamic voice channel", ephemeral=True)
            return

        await voice_channel.edit(name=name)
        await ctx.respond("Renamed the channel", ephemeral=True)

    @vc.command()
    async def lock(self, ctx: d.ApplicationContext, password: d.Option(str, description="Password for the channel")):
        """Set password to lock channel. Remember it, because you won't be reminded of it"""

        member: d.Member = ctx.guild.get_member(ctx.user.id)
        if member is None:
            return
        voice_channel = member.voice.channel

        if voice_channel is None:
            await ctx.respond("You are not in a voice channel", ephemeral=True)
            return

        autovc_list: dict[str, dict] = self.bot.data[AUTOVC_LIST]
        autovc = autovc_list.get(str(voice_channel.id))
        if not autovc:
            await ctx.respond("You are not in a dynamic voice channel", ephemeral=True)
            return

        overwrite = d.PermissionOverwrite()
        overwrite.connect = False
        roles = await ctx.guild.fetch_roles()
        everyone = find(roles, lambda x: x.name == "@everyone")

        await voice_channel.set_permissions(target=roles[everyone], overwrite=overwrite)

        overwrite.connect = True
        you = ctx.guild.get_member(ctx.user.id)
        await voice_channel.set_permissions(target=you, overwrite=overwrite)

        autovc[AutoVC.PASSWORD] = password
        autovc_list[str(voice_channel.id)] = autovc
        self.bot.data[AUTOVC_LIST] = autovc_list

        await ctx.respond("Password set", ephemeral=True)

    @vc.command()
    async def password(
            self,
            ctx: d.ApplicationContext,
            channel: d.Option(d.VoiceChannel, description="Channel you want access to"),
            password: d.Option(str, description="Password for the chosen channel")
    ):
        autovc_list = self.bot.data[AUTOVC_LIST]
        autovc = autovc_list.get(str(channel.id))
        channel: d.VoiceChannel

        if not autovc:
            return ctx.respond("Provided channel isn't dynamic", ephemeral=True)

        if autovc[AutoVC.PASSWORD] == "":
            return ctx.respond("This channel isn't locked", ephemeral=True)

        if autovc[AutoVC.PASSWORD] != password:
            return ctx.respond("Wrong password", ephemeral=True)

        member: d.Member = ctx.guild.get_member(ctx.user.id) or (await ctx.guild.fetch_member(ctx.user.id))

        overwrite = d.PermissionOverwrite()
        overwrite.connect = True

        await channel.set_permissions(target=member, overwrite=overwrite)
        await ctx.respond("Access granted", ephemeral=True)




    @commands.Cog.listener("on_voice_state_update")
    async def detect_trigger_channel(self, member: d.Member, _, new_state: d.VoiceState):
        trigger_id = self.bot.data[AUTOVC_CHANNEL]
        channel: d.VoiceChannel = new_state.channel
        if channel is None:
            return
        if trigger_id is None:
            return
        if channel.id != trigger_id:
            return

        category = channel.category
        presence = member.activity
        new_channel = await AutoVC.create(self.bot, guild=channel.guild, category=category, presence=presence)

        await member.move_to(new_channel.channel)

    @commands.Cog.listener("on_voice_state_update")
    async def detect_empty_channels(self, member, old_state: d.VoiceState, _):
        channel: d.VoiceChannel = old_state.channel
        autovc_list: dict[str, dict] = self.bot.data[AUTOVC_LIST]

        if channel is None:
            return
        if not autovc_list:
            return
        if autovc_list.get(str(channel.id)) is None:
            return
        if len(channel.members) != 0:
            return

        if autovc_list.get(str(channel.id)):
            del autovc_list[str(channel.id)]
            self.bot.data[AUTOVC_LIST] = autovc_list
            await channel.delete()


def setup(bot: MyBot):
    bot.add_cog(DynamicVoiceChatCog(bot))
