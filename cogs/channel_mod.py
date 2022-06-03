import json
import discord
from discord.ext import commands
from discord import Option
from dotenv import dotenv_values
import WarningSystem

env = dotenv_values()


class ChannelModCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.slash_command(name="move-messages", description="Move {n} messages to another channel")
    async def move_messages(
            self,
            ctx: discord.ApplicationContext,
            amount: Option(int, description="Number of messages to move"),
            channel: Option(discord.Member, description="Channel to move messages to")
    ):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)
            return
        if type(channel) != discord.TextChannel:
            await ctx.respond("Provided channel is not a text channel", ephemeral=True)
            return
        if amount < 1:
            await ctx.respond("Cannot move less then 1 message", ephemeral=True)
            return

        await ctx.defer(ephemeral=True)
        amount = int(amount)
        origin_channel = ctx.interaction.channel
        webhook = await discord.TextChannel.create_webhook(channel, name="Move message webhook")

        async for message in origin_channel.history(limit=amount, oldest_first=True):
            author = message.author
            content = message.clean_content
            embeds = message.embeds

            if not content and not embeds:
                continue

            await webhook.send(
                content=content if content else None,
                embeds=embeds if not embeds else None,
                username=author.display_name,
                avatar_url=author.display_avatar.url
            )
            await message.delete()

        await webhook.delete()
        await ctx.respond("Done", ephemeral=True)

    @commands.slash_command(name="purge", description="Purge last {n} messages")
    async def purge(
            self,
            ctx: discord.ApplicationContext,
            number: Option(int, description="Number of messages to delete"),
            user: Option(discord.Member, description="User whose messages you want to remove", required=False)
    ):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)
            return
        if number < 1:
            await ctx.respond("Can't purge less then 1 message", ephemeral=True)
            return

        await ctx.defer(ephemeral=True)
        channel = ctx.interaction.channel
        number = int(number)

        if user:
            def is_user(m):
                return m.author == user

            count = 0
            async for message in channel.history(limit=100).filter(is_user):
                if count == number:
                    break
                await message.delete()
                count += 1
            messages_deleted = count
        else:
            messages_deleted = len(await channel.purge(limit=number))

        await ctx.respond(f"Deleted {messages_deleted} messages", ephemeral=True)

    rules = discord.SlashCommandGroup("rules", "Rules related commands")

    @rules.command(description="Display rules")
    async def display(self, ctx: discord.ApplicationContext):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)
            return

        rules = self.bot.data["rules"]

        embed = discord.Embed(
            title="Rules",
            description=""
        )
        index = 1
        for rule in rules:
            embed.description += f"{index}. {rule}\n"
            index += 1
        embed.colour = discord.Colour.green()
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/icons/625034507577196564/a_888b0c149dbd9dfdacb820e23bb6c183.webp?size=96")
        embed.thumbnail.width = 128
        embed.thumbnail.height = 128

        await ctx.respond(embed=embed)

    @rules.command(description="Set rules")
    async def set(
            self,
            ctx: discord.ApplicationContext,
            rules: Option(str, description="Rules string; Separate rules by double spaces")
    ):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            return await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)

        rules = rules.replace("  ", "\n").split('\n')
        self.bot.data["rules"] = rules

        with open(env["BOT_DATA"], "w") as bot_data_file:
            json.dump(self.bot.data, bot_data_file)

        await ctx.respond("Done", ephemeral=True)

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
                warning_system: WarningSystem.WarningSystem = self.bot.warning_system
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
                warning_system: WarningSystem.WarningSystem = self.bot.warning_system
                await warning_system.add_warning(after.author)


def setup(bot: discord.Bot):
    bot.add_cog(ChannelModCog(bot))
