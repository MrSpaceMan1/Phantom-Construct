import discord
from discord.ext import commands, tasks
from current.utils.MyBot import MyBot


class PollingCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    poll = discord.SlashCommandGroup("poll", "Polls related commands")

    @poll.command(name="create", description="Create a new poll")
    async def create(self, ctx: discord.ApplicationContext):



def setup(bot: MyBot):
    bot.add_cog(PollingCog(bot))
