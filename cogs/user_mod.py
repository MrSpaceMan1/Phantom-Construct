import json
import discord
from discord.ext import commands
from discord import Option
from dotenv import dotenv_values

env = dotenv_values()


class UserModCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.Cog.listener("on_member_update")
    async def bad_nick_suppression(self, before: discord.Member, after: discord.Member):
        new_nick = after.display_name
        cleaned_up_nick = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), new_nick))

        for word in self.bot.data["bad_words"]:
            if word in cleaned_up_nick:
                await after.edit(nick="Change nickname")
                await self.bot.warning_system.add_warning(after)
                return
        if after.display_name != cleaned_up_nick:
            await after.edit(nick=cleaned_up_nick)


def setup(bot: discord.Bot):
    bot.add_cog(UserModCog(bot))
