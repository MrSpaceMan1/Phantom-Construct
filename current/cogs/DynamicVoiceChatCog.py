from typing import List

import discord
from discord import ApplicationContext, Option
from discord.ext import commands
from current.utils.MyBot import MyBot


def list_create(arg):
    if arg is list:
        return arg
    else:
        res = list()
        res.append(arg)
        return res


class DynamicVoiceChatCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    vc = discord.SlashCommandGroup("auto-vc", "Ground of commands to set dynamic voice channels")

    @vc.command(name="set-trigger-channel", description="Set the channel that will trigger channel creation")
    async def set_trigger_channel(
            self,
            ctx: ApplicationContext,
            channel: Option(discord.VoiceChannel, description="Channel to set")
    ):
        perms = ctx.user.guild_permissions
        if not perms.moderate_members:
            await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)
            return

        self.bot.data["autovc_channel"] = int(channel.id)
        await ctx.respond("Channel set", ephemeral=True)

    @vc.command(name="rename", description="Rename channel you are in")
    async def rename(self, ctx: ApplicationContext, name: Option(str)):
        member: discord.Member = ctx.guild.get_member(ctx.user.id)
        if member is None:
            return

        voice_channel = member.voice.channel

        if voice_channel is None:
            await ctx.respond("You are not in a voice channel", ephemeral=True)
            return
        autovc_list = self.bot.data["autovc_list"]
        if voice_channel.id not in autovc_list:
            await ctx.respond("You are not in a dynamic voice channel", ephemeral=True)
            return

        await voice_channel.edit(name=name)
        await ctx.respond("Renamed the channel", ephemeral=True)


    @commands.Cog.listener("on_voice_state_update")
    async def detect_trigger_channel(self, member: discord.Member, _, new_state: discord.VoiceState):
        trigger_id = self.bot.data["autovc_channel"]
        channel: discord.VoiceChannel = new_state.channel
        if channel is None:
            return
        if trigger_id is None:
            return
        if channel.id != trigger_id:
            return

        guild: discord.Guild = channel.guild
        category: discord.CategoryChannel = channel.category
        position: int = (channel.position or guild.get_channel(channel.id).position) + 1
        new_channel = await guild.create_voice_channel("General auto VC", category=category, position=position)

        await member.move_to(new_channel)

        autovc_channels = self.bot.data["autovc_list"]
        if autovc_channels is None:
            self.bot.data["autovc_list"] = [new_channel.id]
        else:
            self.bot.data["autovc_list"] = [new_channel.id, *autovc_channels]


    @commands.Cog.listener("on_voice_state_update")
    async def detect_empty_channels(self, member, old_state: discord.VoiceState, _):
        channel: discord.VoiceChannel = old_state.channel
        autovc_list: List[int] = self.bot.data["autovc_list"]

        if channel is None:
            return
        if autovc_list is None:
            return
        if channel.id not in autovc_list:
            return
        if channel.members != []:
            return

        self.bot.data["autovc_list"] = list(filter(lambda id: id != channel.id, autovc_list))
        await channel.delete()


def setup(bot: MyBot):
    bot.add_cog(DynamicVoiceChatCog(bot))
