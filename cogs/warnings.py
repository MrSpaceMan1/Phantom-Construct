import json
import discord
from discord.ext import commands
from discord import Option, Member, TextChannel, ApplicationContext
from dotenv import dotenv_values

env = dotenv_values()


class WarningsCog(discord.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.slash_command(name="report", description="Report behaviour to staff")
    async def report(
            self,
            ctx: ApplicationContext,
            user: Option(Member, description="User you want to report"),
            report: Option(str, description="Describe behaviour you want to report")
    ):
        if self.bot.data.get("report_channel") is None:
            return await ctx.respond("Report channel is not set. Please ask staff to address this.", ephemeral=True)
        guild = ctx.guild
        report_channel_id = self.bot.data["report_channel"]
        if guild.get_channel(report_channel_id):
            report_channel = guild.get_channel(report_channel_id)
        else:
            report_channel = await guild.fetch_channel(report_channel_id)

        embed: discord.Embed = discord.Embed(title="Report", colour=discord.Colour.red()) \
            .set_thumbnail(url=ctx.interaction.user.display_avatar.url) \
            .add_field(name="Reporter", value=ctx.interaction.user.display_name, inline=False) \
            .add_field(name="Reported", value=user.display_name, inline=False) \
            .add_field(name="Offence", value=report, inline=False)

        await report_channel.send(embed=embed)
        #
        # TODO: Add a button to issue a warning
        #
        await ctx.respond("Thank you for the report", ephemeral=True)

    @commands.slash_command(name="set-report-channel", description="Set report channel")
    async def set_report_channel(
            self,
            ctx: ApplicationContext,
            channel: Option(TextChannel,  description="Channel to set as report channel")
    ):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            return await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)

        self.bot.data["report_channel"] = channel.id

        with open(env["BOT_DATA"], "w") as bot_data:
            json.dump(self.bot.data, bot_data, indent=4)

        await ctx.respond("Channel set", ephemeral=True)

    warnings_group = discord.SlashCommandGroup("warning", "Warnings related commands")

    @warnings_group.command(name="issue", description="Issues a warning to a user")
    async def issue(
            self,
            ctx: ApplicationContext,
            user: Option(Member, description="User to issue a warning")
    ):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            return await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)

        await self.bot.warning_system.add_warning(user=user)
        await ctx.respond("Warning issued", ephemeral=True)

    @warnings_group.command(name="retract",
                            description="Retracts a warning to a user, but does not remove the penalty")
    async def retract(
            self,
            ctx: ApplicationContext,
            user: Option(Member, description="User to retract a warning")
    ):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            return await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)

        await self.bot.warning_system.remove_warning(user=user)
        await ctx.respond("Warning removed", ephemeral=True)

    @commands.user_command(name="Show warnings")
    async def show_user_warnings(self, ctx: ApplicationContext, member: Member):
        warnings = self.bot.warning_system.warnings
        warnings_no = 0 if warnings.get(str(member.id)) is None else warnings[str(member.id)]

        await ctx.respond(f"{member.display_name} has {warnings_no} warnings", ephemeral=True)

    @warnings_group.command(name="warning-list",
                            description="Lists all users with history of warnings")
    async def list(self, ctx: ApplicationContext):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            return await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)

        usr_list = ""
        warnings = self.bot.warning_system.warnings

        for k in warnings:
            usr = await self.bot.get_or_fetch_user(int(k))
            if usr:
                usr_list += f"{usr.display_name}: {warnings[k]}\n"
        await ctx.respond(usr_list, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(WarningsCog(bot))
