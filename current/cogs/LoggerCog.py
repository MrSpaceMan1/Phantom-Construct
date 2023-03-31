from datetime import timezone, datetime, timedelta
from typing import Optional
import discord
from discord import Option, default_permissions
from discord.ext import commands
from current.utils.my_bot import MyBot
from ..utils.constants import LOG_CHANNEL_MESSAGE, LOG_CHANNEL_USER, LOG_CHANNEL_WARNING


class LoggerCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    @commands.slash_command()
    @default_permissions(manage_messages=True)
    async def log_channel_set(
            self,
            ctx: discord.ApplicationContext,
            message_log: Option(discord.TextChannel, description="Set message log channel", required=False),
            user_log: Option(discord.TextChannel, description="Set user log channel", required=False),
            warning_log: Option(discord.TextChannel, description="Set warning/penalty log channel", required=False),
    ):
        """Set different log channels"""
        if message_log:
            self.bot.data[LOG_CHANNEL_MESSAGE] = message_log.id

        if user_log is not None:
            self.bot.data[LOG_CHANNEL_USER] = user_log.id

        if warning_log is not None:
            self.bot.data[LOG_CHANNEL_WARNING] = warning_log.id

        await ctx.respond("Channels set", ephemeral=True)

    @commands.Cog.listener("on_raw_message_edit")
    async def message_edit(self, editData: discord.RawMessageUpdateEvent):
        log_channel_id = self.bot.data[LOG_CHANNEL_MESSAGE]
        log_channel: Optional[discord.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        cached_message: Optional[discord.Message] = editData.cached_message
        guild: Optional[discord.Guild] = self.bot.get_guild(editData.guild_id)
        if guild is None:
            return
        new_message: Optional[discord.Message] = await guild.get_channel(editData.channel_id)\
            .fetch_message(editData.message_id)
        author: discord.User = new_message.author
        if author.bot:
            return

        if not new_message:
            return

        update_embed: discord.Embed = discord.Embed()
        update_embed.url = new_message.jump_url
        update_embed.title = "Message edited"
        update_embed.colour = discord.Colour.orange()
        update_embed.set_author(
            name=f"{author.name}#{author.discriminator}",
            icon_url=author.display_avatar.url,
        )
        update_embed.add_field(name="", value="**Before:** " + (cached_message.content if cached_message else "-"),
                               inline=False)
        update_embed.add_field(name="", value="**+After**: " + new_message.content, inline=False)
        update_embed.timestamp = datetime.now()

        await log_channel.send(embed=update_embed)

    @commands.Cog.listener("on_raw_message_delete")
    async def message_delete(self, deleteData: discord.RawMessageDeleteEvent):
        log_channel_id = self.bot.data[LOG_CHANNEL_MESSAGE]
        log_channel: Optional[discord.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        cached_message: Optional[discord.Message] = deleteData.cached_message
        channel: Optional[discord.TextChannel] = self.bot.get_channel(deleteData.channel_id)

        delete_embed: discord.Embed = discord.Embed()
        delete_embed.title = f"Message deleted in #{channel.name}"
        delete_embed.colour = discord.Colour.red()
        delete_embed.timestamp = datetime.now()

        if cached_message is not None:
            author = cached_message.author

            delete_embed.set_author(
                name=f"{author.name}#{author.discriminator}",
                icon_url=author.display_avatar.url,
            )
            delete_embed.add_field(name="", value=cached_message.content, inline=False)

        delete_embed.add_field(name="", value=f"ID: {deleteData.message_id}")

        await log_channel.send(embed=delete_embed)

    @commands.Cog.listener("on_raw_bulk_message_delete")
    async def message_bulk_delete(self, bulkDeleteData: discord.RawBulkMessageDeleteEvent):
        log_channel_id = self.bot.data[LOG_CHANNEL_MESSAGE]
        log_channel: Optional[discord.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        cached_messages = bulkDeleteData.cached_messages
        channel: Optional[discord.TextChannel] = self.bot.get_channel(bulkDeleteData.channel_id)

        delete_embed = discord.Embed()
        delete_embed.title = f"{len(bulkDeleteData.message_ids)} messages deleted in #{channel.name}"
        delete_embed.description = ""
        delete_embed.colour = discord.Colour.red()
        delete_embed.timestamp = datetime.now()

        if len(cached_messages) != 0:
            for message in cached_messages[:25]:
                name = f"{message.author.name}#{message.author.discriminator}"
                delete_embed.description += f"{name}: {message.clean_content}" \
                                            f"{'' if len(message.embeds) == 0 else f'{len(message.embeds)} embeds'}\n"
            if len(delete_embed.description) > 4096:
                delete_embed.description = delete_embed.description[:4093]+"..."
            return await log_channel.send(embed=delete_embed)
        for message_id in bulkDeleteData.message_ids:
            delete_embed.description += f"{message_id}\n"

    @commands.Cog.listener("on_member_update")
    async def member_update(self, before: discord.Member, after: discord.Member):
        # nickname
        # roles

        log_channel_id = self.bot.data[LOG_CHANNEL_USER]
        log_channel: Optional[discord.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        is_changed = False
        name = f"{after.name}#{after.discriminator}"
        avatar = after.avatar or after.default_avatar
        change = discord.Embed().set_author(name=name, icon_url=avatar.url)

        if before.nick != after.nick:
            change.title = "Nick changed"
            change.add_field(name="Before: ", value=before.nick, inline=True)
            change.add_field(name="After: ", value=after.nick, inline=True)
            change.colour = discord.Colour.orange()
            is_changed = True

        if before.roles != after.roles:
            change.title = "Roles changed"
            before_set = set(before.roles)
            after_set = set(after.roles)
            roles_added = after_set - before_set
            roles_removed = before_set - after_set
            if len(roles_added) != 0:
                parsed_roles = ""
                for role in roles_added:
                    parsed_roles += f"{role.mention}"
                change.add_field(name="Roles added: ", value=parsed_roles)
                change.colour = discord.Colour.green()

            if len(roles_removed) != 0:
                parsed_roles = ""
                for role in roles_removed:
                    parsed_roles += f"{role.mention}"
                change.add_field(name="Roles removed: ", value=parsed_roles)
                change.colour = discord.Colour.red()
            is_changed = True

        if is_changed:
            change.timestamp = datetime.now()
            await log_channel.send(embed=change)

    @commands.Cog.listener("on_user_update")
    async def user_update(self, before: discord.User, after: discord.User):
        # avatar
        # username
        log_channel_id = self.bot.data[LOG_CHANNEL_USER]
        log_channel: Optional[discord.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        is_changed = False
        name = f"{after.name}#{after.discriminator}"
        avatar = after.avatar or after.default_avatar
        change = discord.Embed().set_author(name=name, icon_url=avatar.url)

        if before.avatar != after.avatar:
            change.title = "Avatar changed"
            change.set_image(url=after.avatar.url)
            change.colour = discord.Colour.orange()
            is_changed = True

        if (before.name != after.name) or (before.discriminator != after.discriminator):
            before_name = f"{before.name}#{before.discriminator}"
            change.title = "Username changed"
            change.add_field(name="Before: ", value=before_name)
            change.add_field(name="After: ", value=name)
            change.colour = discord.Colour.orange()
            is_changed = True

        if is_changed:
            change.timestamp = datetime.now()
            await log_channel.send(embed=change)

    @commands.Cog.listener("on_member_ban")
    async def user_ban(self, _, user: discord.Member):
        log_channel_id = self.bot.data["warning_log_channel"]
        log_channel: Optional[discord.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        guild: discord.Guild = user.guild
        time = datetime.now(timezone.utc) - timedelta(seconds=10)
        audit_log: discord.AuditLogEntry = \
            (await guild.audit_logs(limit=1).flatten())[0]

        banned = discord.Embed(title="User banned") \
            .set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.display_avatar.url)
        banned.colour = discord.Colour.red()
        if audit_log.created_at > time and audit_log.action == discord.AuditLogAction.ban:
            banned.description = f"{audit_log.reason}"

        await log_channel.send(embed=banned)

    @commands.Cog.listener("on_member_unban")
    async def user_unban(self, _, user: discord.Member):
        log_channel_id = self.bot.data["warning_log_channel"]
        log_channel: discord.TextChannel or None = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        banned = discord.Embed(title="User unbanned") \
            .set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.display_avatar.url)
        banned.colour = discord.Colour.green()

        await log_channel.send(embed=banned)

    @commands.Cog.listener("on_member_remove")
    async def user_kick_or_leave(self, user: discord.Member):
        user_log_channel_id = self.bot.data["user_log_channel"]
        user_log_channel: discord.TextChannel or None = await self.bot.get_or_fetch_channel(user_log_channel_id)

        warning_log_channel_id = self.bot.data["user_log_channel"]
        warning_log_channel: discord.TextChannel or None = await self.bot.get_or_fetch_channel(warning_log_channel_id)

        if user_log_channel is None or warning_log_channel is None:
            return

        guild: discord.Guild = user.guild
        time = datetime.now(timezone.utc) - timedelta(seconds=10)
        audit_log: discord.AuditLogEntry = \
            (await guild.audit_logs(limit=1).flatten())[0]

        if audit_log.created_at > time and audit_log.action == discord.AuditLogAction.kick:
            avatar = user.avatar or user.default_avatar
            kicked = discord.Embed(title="User kicked") \
                .set_author(name=f"{user.name}#{user.discriminator}", icon_url=avatar.url)
            kicked.colour = discord.Colour.red()
            kicked.description = f"{audit_log.reason}"
            await warning_log_channel.send(embed=kicked)
        elif audit_log.created_at > time and audit_log.action == discord.AuditLogAction.ban:
            pass
        else:
            avatar = user.avatar or user.default_avatar
            left = discord.Embed(title="User left")\
                .set_author(name=f"{user.name}#{user.discriminator}", icon_url=avatar.url)
            left.colour = discord.Colour.red()

            await user_log_channel.send(embed=left)


def setup(bot: MyBot):
    bot.add_cog(LoggerCog(bot))
