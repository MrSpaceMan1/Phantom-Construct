import discord, re
from discord.ext import commands, tasks
from discord import Option
from current.utils.MyBot import MyBot
from current.utils.VolatileStorage import JoinStorage


class MessageFilteringCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot
        self.check_amount_of_joins.start()
        self.index = 0

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

    @commands.Cog.listener("on_voice_state_update")
    async def prevent_join_spam(self, user: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel != after.channel:
            self.bot.session["join"][int(user.id)] += 1

    @tasks.loop(seconds=10.0, count=None)
    async def check_amount_of_joins(self):
        join_dict: JoinStorage = self.bot.session["join"]
        if len(join_dict.keys) > 0:
            for key in join_dict.keys:
                if join_dict[int(key)] >= 6:
                    user: discord.User = await self.bot.get_or_fetch_user(int(key))
                    member = self.bot.is_user_a_member(user)
                    if member is not None:
                        await self.bot.warnings.issue(member)
        self.bot.session["join"].flush()

    @check_amount_of_joins.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()


def setup(bot: MyBot):
    bot.add_cog(MessageFilteringCog(bot))
