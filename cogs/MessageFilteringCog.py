import re
from typing import Optional, Callable
import discord as d
from discord.ext import commands, tasks
from bot.my_bot import MyBot
from bot.volatile_storage import JoinStorage


def check_status(coroutine):
    async def wrapper(self, *args, **kwargs):
        with self.bot.data.access() as state:
            if state.chat_filters.get(coroutine.__name__):
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
        with self.bot.data.access() as state:
            self.bad_words = set(state.bad_words)

    async def filter_message(self, rule: Callable[[d.Message], bool], msg: d.Message) -> bool:
        if msg.channel.type is d.ChannelType.private:
            return False
        guild = msg.guild
        member = await self.bot.is_user_a_member(guild, msg.author)

        with self.bot.data.access() as state:
            roles_whitelist = set(state.roles_whitelist)
            user_whitelist = state.user_whitelist
        is_user_whitelisted = False
        is_role_whitelisted = False

        if member:
            roles = set([role.id for role in member.roles])

            is_user_whitelisted = member.id in user_whitelist
            is_role_whitelisted = len(roles & roles_whitelist) > 0

        if is_role_whitelisted or is_user_whitelisted:
            return False
        elif member and member.bot:
            return False
        elif type(msg.channel) == d.DMChannel:
            return False
        elif msg.channel.type == d.ChannelType.private:
            return False
        else:
            return rule(msg)

    @commands.Cog.listener("on_message")
    @check_status
    async def suppress_bad_words(self, m: d.Message):
        def rule(msg: d.Message) -> bool:
            content = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), msg.clean_content))
            for word in self.bad_words:
                if word in content:
                    return True
            return False

        full_message = await self.bot.get_or_fetch_message(m.channel.id, m.id)
        if await self.filter_message(rule, full_message):
            await m.delete()
            await m.author.send(
                "You are not allowed to use inappropriate words in this server.")

            await self.bot.warnings.issue(full_message.author, full_message.guild)

    @commands.Cog.listener("on_message_edit")
    @check_status
    async def suppress_bad_words_edit(self, _, after):
        def rule(msg: d.Message) -> bool:
            content = "".join(filter(lambda x: x.isalpha() or x.isnumeric(), msg.clean_content))
            for word in self.bad_words:
                if word in content:
                    return True
            return False

        if await self.filter_message(rule, after):
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
                    and len(msg.clean_content()) > 15

        if await self.filter_message(rule, m):
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

        if await self.filter_message(rule, message):
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

        if await self.filter_message(rule, m):
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

        if await self.filter_message(rule, message):
            await message.delete()

    # TODO Validate that this is working
    @commands.Cog.listener("on_message")
    @check_status
    async def prevent_mass_mentions(self, m: d.Message):
        def rule(msg: d.Message) -> bool:
            return len(msg.mentions) > 7 or len(msg.role_mentions) > 4
        full_message = await self.bot.get_or_fetch_message(m.channel.id, m.id)
        if await self.filter_message(rule, full_message):
            await m.delete()
            await self.bot.warnings.issue(full_message.author, full_message.guild)

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
        with self.bot.data.access_write() as write_access:
            val = write_access.chat_filters.get(chat_filter)
            if not val:
                return await ctx.respond("This chat filter doesn't exist", ephemeral=True)
            write_access.chat_filters.update(chat_filter, not val)
        await ctx.respond(f"{chat_filter} is now {'off' if val else 'on'}", ephemeral=True)

    @chat_filters.command()
    async def show(self, ctx: d.ApplicationContext):
        """List filters and their statuses"""
        with self.bot.data.access() as state:
            filters_list = [f"{name}: {'🟩' if on else '🟥'}" for name, on in state.chat_filters.items()]
            parsed_filters = "\n".join(filters_list)
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
        if not (user or role):
            return await ctx.respond("Neither role or user provided", ephemeral=True)
        with self.bot.data.access_write() as write_state:
            if user:
                write_state.user_whitelist.append(user.id)
                msg += "User added to whitelist. "
            if role:
                write_state.roles_whitelist.append(role.id)
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
        if not (user or role):
            return await ctx.respond("Neither role or user provided", ephemeral=True)
        msg = ""
        with self.bot.data.access_write() as write_state:
            if user:
                try:
                    write_state.user_whitelist.remove(user.id)
                    msg += "User added to whitelist. "
                except ValueError:
                    msg += "Provided user isn't on whitelist. "
            if role:
                try:
                    write_state.roles_whitelist.remove(role.id)
                    msg += "Role added to whitelist. "
                except ValueError:
                    msg += "Provided role isn't on whitelist. "
        await ctx.respond(msg, ephemeral=True)

    @chat_filters.command()
    async def whitelist(
            self,
            ctx: d.ApplicationContext
    ):
        """List users and roles in the whitelist"""
        with self.bot.data.access() as state:
            user_ids = state.user_whitelist
            role_ids = state.roles_whitelist

        async def map_users(id_: int) -> Optional[d.User]:
            return await self.bot.get_or_fetch_user(id_)

        async def map_roles(id_: int) -> Optional[d.Role]:
            guild = self.bot.get_guild(ctx.guild.id)
            return guild.get_role(id_)

        users = []
        roles = []

        for id_ in user_ids:
            users.append(await map_users(id_))
        for id_ in role_ids:
            roles.append(await map_roles(id_))

        users = map(lambda x: f"<@{x.id}>", filter(lambda x: x is not None, users))
        roles = map(lambda x: f"<@&{x.id}>", filter(lambda x: x is not None, roles))

        embed = d.Embed()
        embed.add_field(name="Users: ", value=" \n".join(users), inline=False)
        embed.add_field(name="Roles: ", value=" \n".join(roles), inline=False)

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: MyBot):
    bot.add_cog(MessageFilteringCog(bot))
