import re
from typing import Optional, Callable
import discord as d
from discord.ext import commands, tasks
from utils import MyBot, JoinStorage
from utils.constants import *


def check_status(coroutine):
    async def wrapper(self, *args, **kwargs):
        if self.bot.data[CHAT_FILTERS].get(coroutine.__name__):
            await coroutine(self, *args, **kwargs)

    wrapper.__name__ = coroutine.__name__
    return wrapper


def switch_chat_filter_autocomplete(ctx: d.AutocompleteContext) -> list[str]:
    listeners = list(map(lambda x: x[1].__name__, ctx.cog.get_listeners()))
    if ctx.value:
        def is_sub_string(x: str) -> bool:
            return x.find(ctx.value) >= 0

        return list(filter(is_sub_string, listeners))
    return listeners


class MessageFilteringCog(d.Cog):
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

    def filter_message(self, rule: Callable[[d.Message], bool], msg: d.Message) -> bool:
        guild = msg.guild
        member = self.bot.is_user_a_member(msg.author)

        is_user_whitelisted = False
        is_role_whitelisted = False

        if member:
            roles = set(map(lambda x: x.id, member.roles or []))

            user_whitelist: list = self.bot.data[USER_WHITELIST] or []
            roles_whitelist = set(self.bot.data[ROLES_WHITELIST] or [])

            is_user_whitelisted = user_whitelist.count(member.id)
            is_role_whitelisted = len(roles & roles_whitelist)

        if is_role_whitelisted or is_user_whitelisted:
            return False
        elif member and member.bot:
            return False
        elif type(msg.channel) == d.DMChannel:
            return False
        else:
            return rule(msg)

    @commands.Cog.listener("on_message")
    @check_status
    async def suppress_bad_words(self, m: d.Message):
        def rule(msg: d.Message) -> bool:
            content = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), msg.clean_content))
            for word in self.bot.data[BAD_WORDS]:
                if word in content:
                    return True

        if self.filter_message(rule, m):
            await m.delete()
            await m.author.send(
                "You are not allowed to use inappropriate words in this server.")
            await self.bot.warnings.issue(m.author, m.guild)

    @commands.Cog.listener("on_message_edit")
    @check_status
    async def suppress_bad_words_edit(self, _, after):
        def rule(msg: d.Message) -> bool:
            content = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), msg.clean_content))
            for word in self.bot.data[BAD_WORDS]:
                if word in content:
                    return True

        if self.filter_message(rule, after):
            await after.delete()
            await after.author.send(
                "You are not allowed to use inappropriate words in this server.")
            await self.bot.warnings.issue(after.author, after.guild)

    @commands.Cog.listener("on_message")
    @check_status
    async def no_all_caps(self, m: d.Message):
        def rule(msg: d.Message) -> bool:
            return \
                    msg.clean_content.isalpha() \
                    and msg.clean_content == msg.clean_content.upper() \
                    and len(msg.clean_content) > 15

        if self.filter_message(rule, m):
            await m.delete()
            await m.channel.send("Don't use all caps", delete_after=2.0)

    @commands.Cog.listener("on_raw_message_edit")
    @check_status
    async def no_all_caps_edit(self, editData: d.RawMessageUpdateEvent):
        channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(editData.channel_id)
        message = None
        try:
            message: Optional[d.Message] = await channel.fetch_message(editData.message_id)
        except d.NotFound:
            pass

        def rule(msg: d.Message) -> bool:
            # noinspection PyTypeChecker
            clean = "".join(filter(lambda x: x.isalpha(), msg.clean_content))
            return \
                clean.isalpha() \
                and clean == clean.upper() \
                and len(clean) > 20

        if not message:
            return

        if self.filter_message(rule, message):
            await message.delete()
            await message.channel.send("Don't use all caps", delete_after=2.0)

    @commands.Cog.listener("on_message")
    @check_status
    async def no_d_links(self, m: d.Message):
        def rule(msg: d.Message) -> bool:
            match_result = re \
                .search("(https?://)?(d\\.gg/[0-9a-zA-Z]+)(\\?event)?", msg.content)
            _, is_d_link, is_event = match_result.groups() if match_result else (None, None, None)
            return is_d_link and not is_event

        # TODO Match when no https is present

        if self.filter_message(rule, m):
            await m.delete()

    @commands.Cog.listener("on_raw_message_edit")
    @check_status
    async def no_d_links_edit(self, editData: d.RawMessageUpdateEvent):
        channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(editData.channel_id)
        message: Optional[d.Message] = await channel.fetch_message(editData.message_id)

        def rule(msg: d.Message) -> bool:
            match_result = re \
                .search("(https?://d\\.gg/[0-9a-zA-Z]+)(\\?event)?", msg.content)
            is_d_link, is_event = match_result.groups() if match_result else (None, None)
            return is_d_link and not is_event

        if self.filter_message(rule, message):
            await message.delete()

    # TODO Validate that this is working
    @commands.Cog.listener("on_message")
    @check_status
    async def prevent_mass_mentions(self, m: d.Message):
        def rule(msg: d.Message) -> bool:
            return len(msg.mentions) > 7 or len(msg.role_mentions) > 4

        if self.filter_message(rule, m):
            await m.delete()
            await self.bot.warnings.issue(m.author, m.guild)

    @commands.Cog.listener("on_voice_state_update")
    @check_status
    async def prevent_join_spam(self, user: d.Member, before: d.VoiceState, after: d.VoiceState):
        if before.channel != after.channel:
            self.bot.session["join"][int(user.id)] += 1

    @tasks.loop(seconds=10.0, count=None)
    async def check_amount_of_joins(self):
        join_dict: JoinStorage = self.bot.session["join"]
        if len(join_dict.keys) > 0:
            for key in join_dict.keys:
                if join_dict[int(key)] >= 6:
                    user: d.User = await self.bot.get_or_fetch_user(int(key))
                    member = self.bot.is_user_a_member(user)
                    if member is not None:
                        await self.bot.warnings.issue(member, None)
        self.bot.session["join"].flush()

    @check_amount_of_joins.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

    chat_filter_perms = d.Permissions()
    chat_filter_perms.manage_messages = True
    chat_filters = d.SlashCommandGroup(
        name="chat_filters",
        description="Switch on/off chat filters",
        default_member_permissions=chat_filter_perms
    )

    @chat_filters.command()
    async def switch(
            self,
            ctx: d.ApplicationContext,
            chat_filter: d.Option(
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
    async def show(self, ctx: d.ApplicationContext):
        """List filters and their statuses"""
        chat_filters = self.bot.data[CHAT_FILTERS]
        parsed_filters = "".join(
            [f"{filter_name}: {'🟩' if status else '🟥'}\n" for (filter_name, status) in chat_filters.items()])
        await ctx.respond(parsed_filters, ephemeral=True)

    @chat_filters.command()
    async def whitelist_add(
            self,
            ctx: d.ApplicationContext,
            user: d.Option(d.Member, description="Provide user to whitelist", required=False),
            role: d.Option(d.Role, description="Provide role to whitelist", required=False)
    ):
        """Whitelist roles and users"""
        msg = ""
        users = self.bot.data[USER_WHITELIST] or []
        roles = self.bot.data[ROLES_WHITELIST] or []
        if user:
            users.append(user.id)
            self.bot.data[USER_WHITELIST] = users
            msg += "User added to whitelist. "
        if role:
            roles.append(role.id)
            self.bot.data[ROLES_WHITELIST] = roles
            msg += "Role added to whitelist. "

        await ctx.respond(msg, ephemeral=True)

    @chat_filters.command()
    async def whitelist_delete(
            self,
            ctx: d.ApplicationContext,
            user: d.Option(d.Member, description="Provide user to whitelist", required=False),
            role: d.Option(d.Role, description="Provide role to whitelist", required=False)
    ):
        """Remove roles and users from whitelist"""
        users = self.bot.data[USER_WHITELIST]
        roles = self.bot.data[ROLES_WHITELIST]

        msg = ""

        if user:
            try:
                users.pop(users.index(user.id))
                self.bot.data[USER_WHITELIST] = users
                msg += "Provided user removed from whitelist. "
            except ValueError:
                msg += "Provided user isn't on whitelist. "
        if role:
            try:
                roles.pop(roles.index(role.id))
                self.bot.data[ROLES_WHITELIST] = roles
                msg += "Provided role removed form whitelist. "
            except ValueError:
                msg += "Provided role isn't on whitelist. "

        await ctx.respond(msg, ephemeral=True)

    @chat_filters.command()
    async def whitelist(
            self,
            ctx: d.ApplicationContext
    ):
        """List users and roles in the whitelist"""
        user_ids = self.bot.data[USER_WHITELIST] or []
        role_ids = self.bot.data[ROLES_WHITELIST] or []

        async def map_users(id: int) -> Optional[d.User]:
            return await self.bot.get_or_fetch_user(id)

        async def map_roles(id: int) -> Optional[d.Role]:
            guild = self.bot.get_guild(ctx.guild.id)
            return guild.get_role(id)

        users = []
        roles = []

        for id in user_ids:
            users.append(await map_users(id))
        for id in role_ids:
            roles.append(await map_roles(id))

        users = map(lambda x: f"<@{x.id}>", filter(lambda x: x is not None, users))
        roles = map(lambda x: f"<@&{x.id}>", filter(lambda x: x is not None, roles))

        embed = d.Embed()
        embed.add_field(name="Users: ", value=" \n".join(users), inline=False)
        embed.add_field(name="Roles: ", value=" \n".join(roles), inline=False)

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: MyBot):
    bot.add_cog(MessageFilteringCog(bot))
