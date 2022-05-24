import json

import discord
from discord.ext import commands
from discord import option, SlashCommandOptionType as Types
from dotenv import dotenv_values

env = dotenv_values()


class ChannelModCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.slash_command(name="move-messages", description="Move {n} messages to another channel")
    @option(name="amount", type=Types.number, description="Number of messages to move")
    @option(name="channel", type=Types.channel, descripion="Channel to move messages to")
    async def move_messages(self, ctx, amount, channel):
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
    @option(name="number", type=Types.number, description="Number of messages to delete", required=True)
    @option(name="user", type=Types.user, description="User whose messages you want to remove", required=False)
    async def purge(self, ctx, number: int, user: Types.user = None):
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
        messages_deleted = 0

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
    async def display(self, ctx):
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
    @option("rules", type=Types.string, description="Rules string; Separate rules by double spaces")
    async def set(self, ctx, rules: str):
        perms = ctx.interaction.user.guild_permissions
        if not perms.manage_messages:
            await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)
            return

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
                    "You are not allowed to use inappropriate words in this server. You have been issued a warning!")
        #
        #  TODO: Add warning system
        #


def setup(bot: discord.Bot):
    bot.add_cog(ChannelModCog(bot))
