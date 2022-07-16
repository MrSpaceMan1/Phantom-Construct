import discord
from discord import Option
from discord.ext import commands
from current.utils.MyBot import MyBot


class LoggerCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    @commands.slash_command(name="log-channel-set", description="Set different log channels")
    async def log_channel_set(
            self,
            ctx: discord.ApplicationContext,
            message_log: Option(discord.TextChannel, description="Set message log channel", required=False),
            user_log: Option(discord.TextChannel, description="Set user log channel", required=False),
            warning_log: Option(discord.TextChannel, description="Set warning/penalty log channel", required=False),
    ):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            return await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)

        if message_log is not None:
            self.bot.data["message_log_channel"] = message_log.id

        if user_log is not None:
            self.bot.data["user_log_channel"] = user_log.id

        if warning_log is not None:
            self.bot.data["warning_log_channel"] = warning_log.id

        await ctx.respond("Channels set", ephemeral=True)

    @commands.Cog.listener("on_message_edit")
    async def message_edit(self, before, after):
        log_channel_id = self.bot.data["message_log_channel"]
        log_channel: discord.TextChannel or None = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return
        if before.author.bot:
            return
        if before.content == after.content:
            return
        name = f"{before.author.name}#{before.author.discriminator}"
        change_embed = discord.Embed(title="Message edited") \
            .set_author(name=name, icon_url=before.author.avatar.url) \
            .add_field(name="Before", value=before.content, inline=False) \
            .add_field(name="After", value=after.content, inline=False)
        change_embed.colour = discord.Colour.orange()

        await log_channel.send(embed=change_embed)

    @commands.Cog.listener("on_message_delete")
    async def message_delete(self, message):
        log_channel_id = self.bot.data["message_log_channel"]
        log_channel: discord.TextChannel or None = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        name = f"{message.author.name}#{message.author.discriminator}"
        change_embed = discord.Embed(title="Message deleted") \
            .set_author(name=name, icon_url=message.author.avatar.url) \
            .add_field(name="Content", value=message.content, inline=False)
        change_embed.colour = discord.Colour.red()

        await log_channel.send(embed=change_embed)

    @commands.Cog.listener("on_bulk_message_delete")
    async def message_bulk_delete(self, messages):
        log_channel_id = self.bot.data["message_log_channel"]
        log_channel: discord.TextChannel or None = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        change_embed = discord.Embed(title=f"{len(messages)} messages deleted", description="")
        for message in messages[0:25]:
            name = f"{message.author.name}#{message.author.discriminator}"
            change_embed.description += f"{name}: {message.clean_content}" \
                                        f"{'' if len(message.embeds) == 0 else f'{len(message.embeds)} embeds'}\n"
        change_embed.colour = discord.Colour.red()

        await log_channel.send(embed=change_embed)

    @commands.Cog.listener("on_member_update")
    async def user_change(self, before: discord.Member, after: discord.Member):
        log_channel_id = self.bot.data["user_log_channel"]
        log_channel: discord.TextChannel or None = await self.bot.get_or_fetch_channel(log_channel_id)

        if log_channel is None:
            return

        is_changed = False
        name = f"{before.name}#{before.discriminator}"
        avatar = before.avatar or before.default_avatar
        change = discord.Embed()
        change.set_author(name=name, icon_url=avatar.url)

        if before.display_avatar != after.display_avatar:
            change.title = "Avatar changed"
            change.set_image(url=after.display_avatar.url)
            change.colour = discord.Colour.orange()
            is_changed = True

        if before.display_name != after.display_name:
            change.title = "Display name changed"
            change.add_field(name="Before: ", value=before.display_name, inline=False)
            change.add_field(name="After: ", value=after.display_name, inline=False)
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
                change.add_field(name="Roles added", value=parsed_roles)
                change.colour = discord.Colour.green()

            if len(roles_removed) != 0:
                parsed_roles = ""
                for role in roles_removed:
                    parsed_roles += f"{role.mention}"
                change.add_field(name="Roles removed", value=parsed_roles)
                change.colour = discord.Colour.red()
            is_changed = True

        if is_changed:
            await log_channel.send(embed=change)


def setup(bot: MyBot):
    bot.add_cog(LoggerCog(bot))
