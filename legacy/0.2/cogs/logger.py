import json
import discord
from discord.ext import commands
from discord import Embed, TextChannel, Guild, ApplicationContext, Option, Message, Member
from dotenv import dotenv_values

env = dotenv_values()


class LoggerCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.slash_command(name="log-channel-set", description="Set different log channels")
    async def log_channel_set(
            self,
            ctx: ApplicationContext,
            message_log: Option(TextChannel, description="Set message log channel", required=False),
            user_log: Option(TextChannel, description="Set user log channel", required=False),
            warning_log: Option(TextChannel, description="Set warning/penalty log channel", required=False),
    ):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            return await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)

        if message_log is not None:
            self.bot.data["message_log_channel"] = message_log.id

        if user_log is not None:
            self.bot.data["user_log_channel"] = user_log.id

        if warning_log is not None:
            self.bot.data["warning_log_channel"] = warning_log.id

        await ctx.respond("Channels set", ephemeral=True)

    @commands.Cog.listener("on_message_edit")
    async def edit_log(self, before: Message, after: Message):
        if self.bot.data.get("message_log_channel") is None:
            return
        channel_id: int = self.bot.data["message_log_channel"]
        guild: Guild = before.guild

        if guild.get_channel(channel_id) is not None:
            log_channel: TextChannel = guild.get_channel(channel_id)
        else:
            log_channel: TextChannel = await guild.fetch_channel(channel_id)

        embed: discord.Embed = Embed(title="Message edited") \
            .add_field(name="Before: ", value=before.clean_content, inline=False) \
            .add_field(name="After: ", value=after.clean_content, inline=False) \
            .set_author(name=before.author.display_name, icon_url=before.author.display_avatar.url)

        await log_channel.send(embed=embed)

    @commands.Cog.listener("on_member_update")
    async def user_log(self, before: discord.Member, after: discord.Member):
        if self.bot.data.get("user_log_channel") is None:
            return

        channel_id: int = self.bot.data["user_log_channel"]
        guild: Guild = before.guild

        if guild.get_channel(channel_id) is not None:
            log_channel: TextChannel = guild.get_channel(channel_id)
        else:
            log_channel: TextChannel = await guild.fetch_channel(channel_id)

        embed: discord.Embed = Embed(title="User updated") \
            .add_field(name="Before: ", value=before.__repr__(), inline=False) \
            .add_field(name="After: ", value=after.__repr__(), inline=False)

        await log_channel.send(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(LoggerCog(bot))
