import discord, re
from discord.ext import commands
from discord import Option
from current.utils.MyBot import MyBot


class MessageFilteringCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    @commands.Cog.listener("on_message")
    async def suppress_bad_words(self, m):
        if m.author.bot:
            return

        content = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), m.clean_content))
        for word in self.bot.data["bad_words"]:
            if word in content:
                await m.delete()
                await m.author.send(
                    "You are not allowed to use inappropriate words in this server.")
                await self.bot.warnings.issue(m.author)
                break

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
                await self.bot.warnings.issue(after.author)
                break

    @commands.Cog.listener("on_message")
    async def no_all_caps(self, m: discord.Message):
        if m.author.bot:
            return

        if m.clean_content == m.clean_content.upper():
            await m.delete()
            await m.channel.send("Don't use all caps")

    @commands.Cog.listener("on_message_edit")
    async def no_all_caps(self, _, m: discord.Message):
        if m.author.bot:
            return

        if m.clean_content == m.clean_content.upper():
            await m.delete()
            await m.channel.send("Don't use all caps")

    @commands.Cog.listener("on_message")
    async def no_all_caps(self, m: discord.Message):
        if m.author.bot:
            return

        is_discord_link = re.match( """.*https?://discord\.gg/.+""", m.content)

        if is_discord_link:
            await m.delete()

    @commands.Cog.listener("on_message")
    async def prevent_mass_mentions(self, m: discord.Message):
        if m.author.bot:
            return

        if len(m.mentions) > 7:
            await m.delete()
            await self.bot.warnings.issue(m.author)

        if len(m.role_mentions) > 4:
            await m.delete()
            await self.bot.warnings.issue(m.author)


def setup(bot: MyBot):
    bot.add_cog(MessageFilteringCog(bot))
