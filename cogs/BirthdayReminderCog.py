from datetime import date
import discord as d
from discord import default_permissions
from discord.ext import commands
from utils import MyBot

THIS_YEAR = date.today().year

class BirthdayReminderCog(d.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    @commands.slash_command()
    @default_permissions(manage_messages=True)
    async def add_birthday(
            self,
            ctx: d.ApplicationContext,
            month: d.Option(int, description="month of birthday"),
            day: d.Option(int, description="day of birthday"),
            member: d.Option(d.Member, description="Who is the birthday boy/girl/person?")
    ):
        try:
            date(THIS_YEAR, month, day)
            # self.bot.data.

        except ValueError as e:
            await ctx.response.send_message(str(e).capitalize(), ephemeral=True)


def setup(bot: MyBot):
    bot.add_cog(BirthdayReminderCog(bot))
