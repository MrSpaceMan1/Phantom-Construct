import discord
from discord.ext import commands

guilds_ids = [969636569206120498]


class PermissionsCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot


ignore = discord.SlashCommandGroup("ignore", "Ignore channel/role/user etc.")


@ignore.command(name="channel", description="Ignore channels")
async def ignore_channel(ctx, channel: discord.TextChannel):
    await ctx.respond(f"{channel}", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(PermissionsCog(bot))
    bot.add_application_command(ignore)
