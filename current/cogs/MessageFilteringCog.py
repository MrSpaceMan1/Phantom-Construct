import re
from typing import Optional, Coroutine
import inspect
import discord
from discord.ext import commands, tasks
from current.utils.my_bot import MyBot
from current.utils.volatile_storage import JoinStorage
from ..utils.constants import CHAT_FILTERS, BAD_WORDS


def check_status(coroutine):
    async def wrapper(self, *args, **kwargs):
        if self.bot.data[CHAT_FILTERS].get(coroutine.__name__):
            await coroutine(self, *args, **kwargs)
    wrapper.__name__ = coroutine.__name__
    return wrapper


def switch_chat_filter_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
    listeners = list(map(lambda x: x[1].__name__, ctx.cog.get_listeners()))
    if ctx.value:
        def is_sub_string(x: str) -> bool:
            return x.find(ctx.value) >= 0

        return list(filter(is_sub_string, listeners))
    return listeners


class MessageFilteringCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot
        self.check_amount_of_joins.start()
        self.index = 0

        saved_chat_filters: Optional[dict[str, bool]] = self.bot.data[CHAT_FILTERS]
        saved_chat_filters = saved_chat_filters if saved_chat_filters is not None else dict()
        listeners_names = list(map(lambda x: x[1].__name__, self.get_listeners()))
        chat_filters = dict(zip(listeners_names, [False for _ in range(len(listeners_names))]))
        for (x, y) in saved_chat_filters.items():
            chat_filters[x] = y
        self.bot.data["chat_filters"] = chat_filters

    @commands.Cog.listener("on_message")
    @check_status
    async def suppress_bad_words(self, m: discord.Message):
        if not self.bot.data[CHAT_FILTERS].get("suppress_bad_words"):
            return

        if m.author.bot:
            return
        if type(m.channel) == discord.DMChannel:
            return

        content = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), m.clean_content))
        for word in self.bot.data[BAD_WORDS]:
            if word in content:
                await m.delete()
                await m.author.send(
                    "You are not allowed to use inappropriate words in this server.")
                await self.bot.warnings.issue(m.author, m.guild)
                break

    @commands.Cog.listener("on_message_edit")
    @check_status
    async def suppress_bad_words_edit(self, _, after):
        if after.author == self.bot.user:
            return

        content = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), after.clean_content))
        for word in self.bot.data[BAD_WORDS]:
            if word in content:
                await after.delete()
                await after.author.send(
                    "You are not allowed to use inappropriate words in this server.")
                await self.bot.warnings.issue(after.author, after.guild)
                break

    @commands.Cog.listener("on_message")
    @check_status
    async def no_all_caps(self, m: discord.Message):
        if m.author.bot:
            return

        if m.clean_content == m.clean_content.upper():
            await m.delete()
            await m.channel.send("Don't use all caps")

    @commands.Cog.listener("on_message_edit")
    @check_status
    async def no_all_caps_edit(self, _, m: discord.Message):
        if m.author.bot:
            return

        if m.clean_content == m.clean_content.upper() and len(m.clean_content) > 10:
            await m.delete()
            await m.channel.send("Don't use all caps")

    @commands.Cog.listener("on_message")
    @check_status
    async def no_discord_links(self, m: discord.Message):
        if m.author.bot:
            return

        match_result = re \
            .search("(https?://discord\\.gg/[0-9a-zA-Z]+)(\\?event)?", m.content)
        is_discord_link, is_event = match_result.groups() if match_result else (None, None)
        if is_discord_link and not is_event:
            await m.delete()

    @commands.Cog.listener("on_message")
    @check_status
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
    @check_status
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

    chat_filter_perms = discord.Permissions()
    chat_filter_perms.manage_messages = True
    chat_filters = discord.SlashCommandGroup(
        name="chat_filters",
        description="Switch on/off chat filters",
        default_member_permissions=chat_filter_perms
    )

    @chat_filters.command()
    async def switch(
            self,
            ctx: discord.ApplicationContext,
            chat_filter: discord.Option(
                str,
                description="Chat filter to switch on/off",
                autocomplete=switch_chat_filter_autocomplete
            )
    ):
        """Switch filter on/off"""
        filters: dict[str, bool] = self.bot.data[CHAT_FILTERS]
        value = filters.get(chat_filter)
        if value is None:
            return await ctx.respond("This chat filter doesn't exist", ephemeral=True)
        filters[chat_filter] = not value
        self.bot.data[CHAT_FILTERS] = filters

        await ctx.respond(f"{chat_filter} is now {'off' if value else 'on'}", ephemeral=True)

    @chat_filters.command()
    async def show(self, ctx: discord.ApplicationContext):
        """List filters and their statuses"""
        chat_filters = self.bot.data[CHAT_FILTERS]
        parsed_filters = "".join(
            [f"{filter_name}: {'🟩' if status else '🟥'}\n" for (filter_name, status) in chat_filters.items()])
        await ctx.respond(parsed_filters, ephemeral=True)


def setup(bot: MyBot):
    bot.add_cog(MessageFilteringCog(bot))
