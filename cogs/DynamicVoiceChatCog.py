import datetime
from typing import cast, TYPE_CHECKING

import discord as d
from aiohttp.abc import HTTPException
from discord.ext import commands

from data_classes.dynamic_voicechat_data import DynamicVoicechatRequests
from entities.autovc import AutoVC
from utils.iterable_methods import find
from views import AutoVcControlView, AutoVcRequestView, AutoVcConfigView


if TYPE_CHECKING:
    from bot.my_bot import MyBot

class DynamicVoiceChatCog(d.Cog):
    def __init__(self, bot: "MyBot"):
        self.bot: "MyBot" = bot
        self.trigger_channel: d.VoiceChannel = None

    permissions = d.Permissions()
    permissions.connect = True
    vc = d.SlashCommandGroup(
        "auto-vc",
        "Group of commands to set dynamic voice channels",
        default_member_permissions=permissions
    )

    @d.default_permissions(manage_channels=True)
    @d.command(name="autovc-configure")
    async def configure(
            self,
            ctx: d.ApplicationContext
    ):
        """Set the channel that will trigger channel creation"""
        with self.bot.data.access() as state:
            base_role = None
            if base_role_id := state.autovc_config.base_role_id:
                base_role = ctx.guild.get_role(base_role_id)

            trigger_channel = None
            if trigger_channel_id := state.autovc_config.trigger_channel_id:
                trigger_channel = await self.bot.get_or_fetch_channel(trigger_channel_id)

        await ctx.respond(
            "Configure",
            view=AutoVcConfigView(self.bot, base_role=base_role, trigger_channel=trigger_channel),
            ephemeral=True
        )

    @vc.command(name="rename", description="Rename channel you are in")
    async def rename(
            self,
            ctx: d.ApplicationContext,
            name: d.Option(str, description="Overrides current channel name")
    ):
        await AutoVC.rename(name, interaction=ctx.interaction, bot=self.bot)

    @vc.command()
    async def lock(
            self,
            ctx: d.ApplicationContext,
    ):
        """Toggle lock of the channel."""
        await ctx.defer(ephemeral=True, invisible=True)
        return await AutoVC.lock(ctx.interaction, self.bot)


    @vc.command()
    async def join(self, ctx: d.ApplicationContext, channel_to: d.Option(d.VoiceChannel, name="channel", description="Channel you want to join")):
        """Request to join dynamic voice channel"""
        current_user = ctx.user
        current_user_id = current_user.id
        current_vc = getattr(current_user.voice, "channel", None)
        channel_to: d.VoiceChannel = cast(d.VoiceChannel, channel_to)

        if current_vc is None:
            return await ctx.respond("You need to be in voice channel to request join.", ephemeral=True)

        with self.bot.data.access_write() as state:
            autovc_data = state.autovc_list.get(str(channel_to.id), None)

            if not autovc_data:
                return await ctx.respond("Cannot request to join. It's not an auto voice chat. ", ephemeral=True)

            index = find(autovc_data.requests, lambda r: r.user_id == current_user_id)
            if index >= 0:
                if autovc_data.requests[index].timeout > datetime.datetime.now().timestamp():
                    return await ctx.respond("You have already requested to join. Await response.", ephemeral=True)

            request_view = AutoVcRequestView(self.bot)
            msg = await channel_to.send(
                f"# {current_user.display_name} wants to join your channel. <@{autovc_data.owner_id}>",
                view=request_view,
                delete_after=60 * 5
            )


            in_ten_minutes = datetime.datetime.now() + datetime.timedelta(minutes=10)
            if index >= 0:
                autovc_data.requests[index].timeout = in_ten_minutes.timestamp()
            else:
                autovc_data.requests.append(DynamicVoicechatRequests.from_tuple(current_user_id, in_ten_minutes.timestamp(), message_id=msg.id))

        return await ctx.respond("Request sent.", ephemeral=True)

    @commands.Cog.listener("on_voice_state_update")
    async def detect_trigger_channel(self, member: d.Member, _, new_state: d.VoiceState):
        if not self.trigger_channel:
            with self.bot.data.access() as state:
                if not state.autovc_config.trigger_channel_id:
                    return
                if trigger_channel := (await self.bot.get_or_fetch_channel(state.autovc_config.trigger_channel_id)):
                    self.trigger_channel = trigger_channel
                else:
                    return

        channel: d.VoiceChannel = new_state.channel
        if channel is None:
            return
        if channel != self.trigger_channel:
            return

        new_channel = await AutoVC.create(self.bot, member)
        await member.move_to(new_channel.channel)

    @commands.Cog.listener("on_voice_state_update")
    async def detect_empty_channels(self, member, old_state: d.VoiceState, _):
        channel = old_state.channel
        if channel is None:
            return

        with self.bot.data.access_write() as state:
            autovc_list = state.autovc_list
            if not autovc_list:
                return
            if autovc_list.get(str(channel.id)) is None:
                return
            if len(channel.members) != 0:
                return

            try:
                await channel.delete()
                del state.autovc_list[str(channel.id)]
            except d.NotFound:
                print("Channel already gone")
                del state.autovc_list[str(channel.id)]
            except d.HTTPException:
                print("Couldn't delete the channel")

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(AutoVcRequestView(self.bot))
        self.bot.add_view(AutoVcControlView(self.bot))


def setup(bot: "MyBot"):
    bot.add_cog(DynamicVoiceChatCog(bot))
