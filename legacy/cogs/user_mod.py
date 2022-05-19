import discord
from discord import option
from discord import SlashCommandOptionType as types
from discord.ext import commands
from legacy.utils import reply, no_premissions


class UserModCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.slash_command(name="badname", description="Changes name to signify bad name")
    @option(name="user", type=types.user, required=True)
    async def badname(self, ctx, user):
        if not ctx.interaction.user.guild_permissions.manage_nicknames:
            await no_premissions(ctx)
            return

        await ctx.defer(ephemeral=True)
        await user.send(f"Your name in {ctx.interaction.guild.name} server is inappropriate. Please change it.")
        await user.edit(nick="PLEASE USE A PROPER NAME")
        await reply(ctx, "Done")


def setup(bot: discord.Bot):
    bot.add_cog(UserModCog(bot))
