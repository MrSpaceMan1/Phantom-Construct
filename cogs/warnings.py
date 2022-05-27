import json

import discord
from discord.ext import commands
from discord import Option
from dotenv import dotenv_values

env = dotenv_values()


class WarningsCog(discord.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.slash_command(name="report", description="Report behaviour to staff")
    async def report(
            self,
            ctx: discord.ApplicationContext,
            user: discord.Member = Option(description="User you want to report"),
            report: str = Option(description="Describe behaviour you want to report")
    ):
        if self.bot.data.get("report_channel") is None:
            return await ctx.respond("Report channel is not set. Please ask staff to address this.", ephemeral=True)
        guild = ctx.guild
        report_channel_id = self.bot.data["report_channel"]
        if guild.get_channel(report_channel_id):
            report_channel = guild.get_channel(report_channel_id)
        else:
            report_channel = await guild.fetch_channel(report_channel_id)

        await report_channel.send(f"User {ctx.interaction.user} has sent report. Here are it's content.\n"
                                  f"Offender: {user}, Offensive behaviour: {report}")
        await ctx.respond("Thank you for the report", ephemeral=True)

    @commands.slash_command(name="set-report-channel", description="Set report channel")
    async def set_report_channel(
            self,
            ctx: discord.ApplicationContext,
            channel: discord.TextChannel = Option(description="Channel to set as report channel")
    ):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            return await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)

        self.bot.data["report_channel"] = channel.id

        with open(env["BOT_DATA"], "w") as bot_data:
            json.dump(self.bot.data, bot_data, indent=4)

        await ctx.respond("Channel set", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(WarningsCog(bot))
