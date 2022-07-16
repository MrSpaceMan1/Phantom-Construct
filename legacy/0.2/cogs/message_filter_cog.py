import discord
from discord.ext import commands
from discord import Cog


class MessageFilterCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def suppress_bad_words(self, m):
        if m.author == self.bot.user:
            return

        content = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), m.clean_content))
        for word in self.bot.data["bad_words"]:
            if word in content:
                await m.delete()
                await m.author.send(
                    "You are not allowed to use inappropriate words in this server.")
                warning_system = self.bot.warning_system
                await warning_system.add_warning(m.author)

    @commands.Cog.listener("on_message_edit")
    async def suppress_bad_word(self, _, after):
        if after.author == self.bot.user:
            return

        content = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), after.clean_content))
        for word in self.bot.data["bad_words"]:
            if word in content:
                await after.delete()
                await after.author.send(
                    "You are not allowed to use inappropriate words in this server.")
                warning_system = self.bot.warning_system
                await warning_system.add_warning(after.author)
