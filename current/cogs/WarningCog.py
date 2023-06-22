import discord
from discord.ext import commands
from discord import Option, default_permissions
from current.utils.constants import REPORT_CHANNEL
from current.utils.my_bot import MyBot


class WarningCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    warning = discord.SlashCommandGroup("warning", "Commands related to warning system")

    @warning.command(name="issue", description="Issue a warning to user")
    @default_permissions(moderate_members=True)
    async def issue(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.Member, description="User to issue warning to")
    ):
        await self.bot.warnings.issue(user, ctx.guild)
        await ctx.respond("Warning issued", ephemeral=True)

    @warning.command()
    @default_permissions(moderate_members=True)
    async def retract(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.Member, description="User to issue warning to")
    ):
        """Retract a warning from user"""
        await self.bot.warnings.retract(user)
        await ctx.respond("Warning retracted", ephemeral=True)

    @warning.command()
    @default_permissions(moderate_members=True)
    async def list(self, ctx: discord.ApplicationContext):
        """List all users with warnings"""
        warnings_dict: dict = self.bot.warnings()
        formatted_list = ""
        for uid, warnings in warnings_dict.items():
            if warnings == 0:
                continue
            formatted_list += f"<@{uid}>: {warnings}\n"

        if formatted_list == "":
            formatted_list = "No active warnings"
        await ctx.respond(formatted_list, ephemeral=True)

    @commands.slash_command()
    async def report(
        self,
        ctx: discord.ApplicationContext,
        user_to_report: Option(discord.Member, description="Provide the user to report"),
        report: Option(str, description="Provide description of the situation")
    ):
        """Report user. Please provide a reason for the report"""
        report_channel_id = self.bot.data[REPORT_CHANNEL]
        report_channel = await self.bot.get_or_fetch_channel(report_channel_id)

        if report_channel is None:
            await ctx.respond("Report channel not set. Please contact staff")
            return

        reporter_avatar = ctx.user.avatar or ctx.user.default_avatar
        reported_avatar = user_to_report.avatar or user_to_report.default_avatar

        embed: discord.Embed = discord.Embed(colour=discord.Colour.red()) \
            .set_author(name=f"{ctx.user.name}#{ctx.user.discriminator}", icon_url=reporter_avatar.url) \
            .set_thumbnail(url=reported_avatar.url) \
            .add_field(name="Reported", value=user_to_report.mention, inline=False) \
            .add_field(name="Offence", value=report, inline=False)

        await report_channel.send(embed=embed)
        await ctx.respond("Report sent. Thank you for informing us.", ephemeral=True)


def setup(bot: MyBot):
    bot.add_cog(WarningCog(bot))
