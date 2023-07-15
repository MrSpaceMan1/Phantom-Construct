from datetime import timezone, datetime, timedelta
from typing import Optional
import discord as d
from discord.ext import commands
from utils import MyBot
from utils.constants import *


class LoggerCog(d.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    @commands.slash_command()
    @d.default_permissions(manage_messages=True)
    async def log_channel_set(
            self,
            ctx: d.ApplicationContext,
            message_log: d.Option(d.TextChannel, description="Set message log channel") = None,
            user_log: d.Option(d.TextChannel, description="Set user log channel") = None,
            warning_log: d.Option(d.TextChannel, description="Set warning/penalty log channel") = None,
            voice_log: d.Option(d.TextChannel, description="Set voice activity log channel") = None
    ):
        """Set different log channels"""
        if message_log:
            self.bot.data[LOG_CHANNEL_MESSAGE] = message_log.id

        if user_log is not None:
            self.bot.data[LOG_CHANNEL_USER] = user_log.id

        if warning_log is not None:
            self.bot.data[LOG_CHANNEL_WARNING] = warning_log.id

        if voice_log is not None:
            self.bot.data[LOG_CHANNEL_VOICE] = voice_log.id

        await ctx.respond("Channels set", ephemeral=True)

    @commands.Cog.listener("on_raw_message_edit")
    async def message_edit(self, editData: d.RawMessageUpdateEvent):
        log_channel_id = self.bot.data[LOG_CHANNEL_MESSAGE]
        log_channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        cached_message: Optional[d.Message] = editData.cached_message
        guild: Optional[d.Guild] = self.bot.get_guild(editData.guild_id)
        if guild is None:
            return
        new_message: Optional[d.Message] = await guild.get_channel(editData.channel_id) \
            .fetch_message(editData.message_id)
        author: d.User = new_message.author
        if author.bot:
            return

        if not new_message:
            return

        avatar = author.avatar or author.default_avatar

        update_embed: d.Embed = d.Embed()
        update_embed.url = new_message.jump_url
        update_embed.title = "Message edited"
        update_embed.colour = d.Colour.orange()
        update_embed.set_author(
            name=f"<@{author.id}>",
            icon_url=avatar.url,
        )

        before = "**Before:** " + (cached_message.content if cached_message else "-")
        after = "**+After**: " + new_message.content

        update_embed.add_field(name="", value=before[:1024],
                               inline=False)
        update_embed.add_field(name="", value=after[:1024], inline=False)
        update_embed.timestamp = datetime.now()

        await log_channel.send(embed=update_embed)

    @commands.Cog.listener("on_raw_message_delete")
    async def message_delete(self, deleteData: d.RawMessageDeleteEvent):
        log_channel_id = self.bot.data[LOG_CHANNEL_MESSAGE]
        log_channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        cached_message: Optional[d.Message] = deleteData.cached_message
        channel: Optional[d.TextChannel] = self.bot.get_channel(deleteData.channel_id)

        match cached_message:
            case None:
                pass
            case x if x.author.bot:
                return

        delete_embed: d.Embed = d.Embed()
        delete_embed.title = f"Message deleted in #{channel.name}"
        delete_embed.colour = d.Colour.red()
        delete_embed.timestamp = datetime.now()

        if cached_message is not None:
            author = cached_message.author
            avatar = author.avatar or author.default_avatar
            delete_embed.set_author(
                name=f"{author.name}",
                icon_url=avatar.url,
            )
            delete_embed.add_field(name="", value=cached_message.content, inline=False)

        delete_embed.add_field(name="", value=f"ID: {deleteData.message_id}")

        await log_channel.send(embed=delete_embed)

    @commands.Cog.listener("on_raw_bulk_message_delete")
    async def message_bulk_delete(self, bulkDeleteData: d.RawBulkMessageDeleteEvent):
        log_channel_id = self.bot.data[LOG_CHANNEL_MESSAGE]
        log_channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        cached_messages = bulkDeleteData.cached_messages
        channel: Optional[d.TextChannel] = self.bot.get_channel(bulkDeleteData.channel_id)

        delete_embed = d.Embed()
        delete_embed.title = f"{len(bulkDeleteData.message_ids)} messages deleted in #{channel.name}"
        delete_embed.description = ""
        delete_embed.colour = d.Colour.red()
        delete_embed.timestamp = datetime.now()

        if len(cached_messages) != 0:
            for message in cached_messages[:25]:
                author = message.author
                name = f"<@{author.id}>"
                delete_embed.description += f"{name}: {message.clean_content}" \
                                            f"{'' if len(message.embeds) == 0 else f'{len(message.embeds)} embeds'}\n"
            if len(delete_embed.description) > 4096:
                delete_embed.description = delete_embed.description[:4093] + "..."
            return await log_channel.send(embed=delete_embed)
        for message_id in bulkDeleteData.message_ids:
            delete_embed.description += f"{message_id}\n"

    @commands.Cog.listener("on_member_update")
    async def member_update(self, before: d.Member, after: d.Member):
        # nickname
        # roles

        log_channel_id = self.bot.data[LOG_CHANNEL_USER]
        log_channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        is_changed = False
        name = f"{after.name}"
        avatar = after.avatar or after.default_avatar
        change = d.Embed().set_author(name=name, icon_url=avatar.url)

        if before.nick != after.nick:
            change.title = "Nick changed"
            change.add_field(name="Before: ", value=before.nick, inline=True)
            change.add_field(name="After: ", value=after.nick, inline=True)
            change.colour = d.Colour.orange()
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
                change.colour = d.Colour.green()

            if len(roles_removed) != 0:
                parsed_roles = ""
                for role in roles_removed:
                    parsed_roles += f"{role.mention}"
                change.add_field(name="Roles removed: ", value=parsed_roles)
                change.colour = d.Colour.red()
            is_changed = True

        if is_changed:
            change.timestamp = datetime.now()
            await log_channel.send(embed=change)

    @commands.Cog.listener("on_user_update")
    async def user_update(self, before: d.User, after: d.User):
        # avatar
        # username
        log_channel_id = self.bot.data[LOG_CHANNEL_USER]
        log_channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        is_changed = False
        name = f"{after.name}"
        avatar = after.avatar or after.default_avatar
        change = d.Embed().set_author(name=name, icon_url=avatar.url)

        if before.avatar != after.avatar:
            change.title = "Avatar changed"
            change.set_image(url=after.avatar.url)
            change.colour = d.Colour.orange()
            is_changed = True

        if (before.name != after.name) or (before.discriminator != after.discriminator):
            before_name = f"{before.name}"
            change.title = "Username changed"
            change.add_field(name="Before: ", value=before_name)
            change.add_field(name="After: ", value=name)
            change.colour = d.Colour.orange()
            is_changed = True

        if is_changed:
            change.timestamp = datetime.now()
            await log_channel.send(embed=change)

    @commands.Cog.listener("on_member_ban")
    async def user_ban(self, _, user: d.Member):
        log_channel_id = self.bot.data[LOG_CHANNEL_WARNING]
        log_channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        guild: d.Guild = user.guild
        time = datetime.now(timezone.utc) - timedelta(seconds=10)
        audit_log: d.AuditLogEntry = \
            (await guild.audit_logs(limit=1).flatten())[0]

        banned = d.Embed(title="User banned") \
            .set_author(name=f"<@{user.id}>", icon_url=user.display_avatar.url)
        banned.colour = d.Colour.red()
        banned.timestamp = datetime.now()
        if audit_log.created_at > time and audit_log.action == d.AuditLogAction.ban:
            banned.description = f"{audit_log.reason}"

        await log_channel.send(embed=banned)

    @commands.Cog.listener("on_member_unban")
    async def user_unban(self, _, user: d.Member):
        log_channel_id = self.bot.data[LOG_CHANNEL_WARNING]
        log_channel: d.TextChannel or None = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        banned = d.Embed(title="User unbanned") \
            .set_author(name=f"<@{user.id}>", icon_url=user.display_avatar.url)
        banned.colour = d.Colour.green()
        banned.timestamp = datetime.now()

        await log_channel.send(embed=banned)

    @commands.Cog.listener("on_member_remove")
    async def user_kick_or_leave(self, user: d.Member):
        user_log_channel_id = self.bot.data[LOG_CHANNEL_USER]
        user_log_channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(user_log_channel_id)

        warning_log_channel_id = self.bot.data[LOG_CHANNEL_WARNING]
        warning_log_channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(warning_log_channel_id)

        if user_log_channel is None or warning_log_channel is None:
            return

        guild: d.Guild = user.guild
        time = datetime.now(timezone.utc) - timedelta(seconds=10)
        audit_log: d.AuditLogEntry = \
            (await guild.audit_logs(limit=1).flatten())[0]

        if audit_log.created_at > time and audit_log.action == d.AuditLogAction.kick:
            avatar = user.avatar or user.default_avatar
            kicked = d.Embed(title="User kicked") \
                .set_author(name=f"<@{user.id}>", icon_url=avatar.url)
            kicked.colour = d.Colour.red()
            kicked.description = f"{audit_log.reason}"
            kicked.timestamp = datetime.now()
            await warning_log_channel.send(embed=kicked)
        elif audit_log.created_at > time and audit_log.action == d.AuditLogAction.ban:
            pass
        else:
            avatar = user.avatar or user.default_avatar
            left = d.Embed(title="User left") \
                .set_author(name=f"<@{user.id}>", icon_url=avatar.url)
            left.colour = d.Colour.red()
            left.timestamp = datetime.now()

            await user_log_channel.send(embed=left)

    @commands.Cog.listener("on_voice_state_update")
    async def user_join_left_voice_chat(self, member: d.Member, before: d.VoiceState, after: d.VoiceState):
        voice_log_channel_id = self.bot.data[LOG_CHANNEL_VOICE]
        voice_log_channel: Optional[d.TextChannel] = await self.bot.get_or_fetch_channel(voice_log_channel_id)

        if voice_log_channel is None:
            return

        avatar = member.avatar.url
        name = member.name

        channel: d.VoiceChannel = after.channel

        embed: d.Embed = d.Embed()
        embed.set_author(name=name, icon_url=avatar)
        embed.timestamp = datetime.now()

        if channel and not before.channel:
            embed.title = "User joined voice channel"
            embed.colour = d.Colour.green()
            embed.add_field(
                name="",
                value=f"**{name}** joined {channel.name}"
            )
        elif before.channel and channel:
            embed.title = "User changed voice channel"
            embed.colour = d.Colour.orange()
            embed.add_field(
                name="",
                value=f"**{name}** joined {channel.name}"
            )
        else:
            embed.title = "User left voice channel"
            embed.colour = d.Colour.red()
            embed.add_field(
                name="",
                value=f"**{name}** left {before.channel.name}"
            )

        await voice_log_channel.send(embed=embed)


def setup(bot: MyBot):
    bot.add_cog(LoggerCog(bot))
