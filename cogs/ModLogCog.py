import logging
import itertools
import operator
from typing import TYPE_CHECKING, Any, Callable

import discord as d
from discord.ext import commands, tasks

from entities.auditlogformater import AuditLogEntryFormater

if TYPE_CHECKING:
    from bot import my_bot

logger = logging.getLogger(__name__)

class ModLogCog(d.Cog):
    def __init__(self, bot: "my_bot.MyBot"):
        self.bot = bot
        self.inbox: list[d.AuditLogEntry] = []
        self.process_audit_logs.start()

    @commands.slash_command()
    @d.default_permissions(manage_messages=True)
    async def set_mod_log_channel(
        self,
        ctx: "d.ApplicationContext",
        channel: d.Option(d.TextChannel, description="Set mod log channel")
    ):
        channel: d.TextChannel
        with self.bot.data.access_write() as write_state:
            write_state.mod_log_channel = channel.id

        await ctx.respond("Channel set", ephemeral=True)

    @commands.slash_command()
    @d.default_permissions(manage_messages=True)
    async def set_mod_log_role(
            self,
            ctx: "d.ApplicationContext",
            role: d.Option(d.SlashCommandOptionType.role, description="Set mod log channel")
    ):
        role: d.Role
        with self.bot.data.access_write() as write_state:
            write_state.mod_log_role = role.id

        await ctx.respond("Role set", ephemeral=True)

    @commands.Cog.listener("on_raw_audit_log_entry")
    async def log_audit_log_entry(self, payload: "d.RawAuditLogEntryEvent"):

        with self.bot.data.access() as state:
            if not (state.mod_log_channel and state.mod_log_role):
                return

        data = payload.data
        guild = self.bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        if not guild or not member:
            return

        audit_log_entry = d.AuditLogEntry(users={data["user_id"]: member}, data=data, guild=guild)
        self.inbox.append(audit_log_entry)



    @tasks.loop(seconds=10)
    async def process_audit_logs(self):
        channel = None
        with self.bot.data.access() as state:
            if not (state.mod_log_channel and state.mod_log_role):
                return
            channel: "d.TextChannel" = await self.bot.get_or_fetch_channel(state.mod_log_channel)
        from utils.audit_diff_accumulator import accumulate_changes
        formatters: list[AuditLogEntryFormater] = []
        for key, group in itertools.groupby(self.inbox, operator.attrgetter("action", "target", "extra")):
            action, _, _ = key
            cumulative_log = accumulate_changes(list(group))
            formatters.append(AuditLogEntryFormater(entry=cumulative_log))

        self.inbox=[]
        webhooks = {}
        for formater in formatters:
            avatar = (await formater.entry.user.avatar.read()) if formater.entry.user.avatar else None
            if msg := formater.format():
                webhook = webhooks.get(formater.entry.guild, None)
                if not webhook:
                    webhook = await channel.create_webhook(name=formater.entry.user.display_name, avatar=avatar)
                    webhooks[formater.entry.guild] = webhook
                await webhook.send(msg)

        for webhook in webhooks.values():
            await webhook.delete()

def setup(bot: "my_bot.MyBot"):
    bot.add_cog(ModLogCog(bot))