import json
import discord
from discord import Option, option, SlashCommandOptionType as types
from discord.ext import commands
from dotenv import dotenv_values
from legacy.utils import reply, no_premissions, is_ignored, BadWords

guilds_ids = [969636569206120498]

env = dotenv_values(".env")


class ChannelModCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.slash_command(
        name="move-messages",
        description="Move n last messages",
        number=Option(int, "Number of messages to move", required=True),
        channel=Option(discord.abc.GuildChannel, "Channel to move messages to", required=True),
        guild_ids=guilds_ids)
    async def move_messages(self, ctx, number: int, channel: discord.TextChannel):

        await ctx.defer(ephemeral=True)

        move_from_channel = ctx.channel
        move_to_channel = channel
        history = await move_from_channel.history(limit=number).flatten()

        if number > len(history):
            number = len(history)

        for a in range(number - 1, -1, -1):
            i = history[a]

            webhook = await discord.TextChannel.create_webhook(move_to_channel, name="MoveWebhook")

            await webhook.send(i.content, username=i.author.name, avatar_url=i.author.display_avatar)
            await webhook.delete()
            await i.delete()

        await reply(ctx, "Done")
        return

    @commands.slash_command(
        name="purge",
        description="Purge n last messages",
        guild_ids=guilds_ids)
    @option(
        name="user",
        type=types.user,
        description="User whose messages you want gone",
        required=False)
    @option(name="number",
            type=types.number,
            description="Number of messages to delete",
            required=True)
    async def purge(self, ctx, number: int, user: discord.SlashCommandOptionType.user = None):
        await ctx.defer(ephemeral=True)

        is_ignored(ctx.interaction.channel, ctx.interaction.user)

        number = int(number)
        users_permissions = ctx.interaction.user.guild_permissions
        if not users_permissions.manage_messages:
            await no_premissions(ctx)
            return

        channel_to_purge = ctx.channel

        def pred(m):
            return m.author == user

        if user is None:
            await channel_to_purge.purge(limit=number, check=lambda x: True)
        else:
            message_counter = 0
            messages = ctx.interaction.channel.history(limit=100).filter(pred)
            async for i in messages:
                if message_counter == number:
                    break
                await i.delete()
                message_counter += 1
        await reply(ctx, "Done")
        return

    rules = discord.SlashCommandGroup("rules", "Rules commands")

    @rules.command(description="Set rules. Provide text with with double spaces as newlines")
    @option(name="rules", type=types.string)
    async def set(self, ctx, rules_to_set: str):
        if not ctx.interaction.user.guild_permissions.moderate_members:
            await no_premissions(ctx)
            return

        await ctx.defer(ephemeral=True)

        data = None
        with open("/legacy/bot_data.json", "r") as bot_data:
            data = json.load(bot_data)
            data["rules"] = rules_to_set.split("  ")

            with open("/legacy/bot_data.json", "w") as bot_data2:
                json.dump(data, bot_data2, indent=4)

        await reply(ctx, "Done")

    @rules.command(description="Display the rules")
    async def display(self, ctx):
        embed = discord.Embed(
            title="Rules",
            description=""
        )
        embed.colour = discord.Colour.green()
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/icons/625034507577196564/a_888b0c149dbd9dfdacb820e23bb6c183.webp?size=96")
        embed.thumbnail.width = 128
        embed.thumbnail.height = 128

        with open("/legacy/bot_data.json", "r") as bot_data:
            data = json.load(bot_data)
            rule_no = 1
            for rule in data["rules"]:
                embed.description += f"{rule_no}. {rule}\n"
                rule_no += 1
            bot_data.close()

        await ctx.respond(embed=embed)

    @commands.slash_command(name="bad-words",
                            description="Set list of bad words. Provide list of words seperated by spaces")
    @option(name="words", type=types.string)
    async def bad_words(self, ctx, words):
        with open(env["BOT_DATA"], 'r') as bot_data:
            data = json.load(bot_data)
            data["bad_words"] = words.split(" ")
            bw = BadWords.instance
            bw.words = words.split(" ")

        with open(env["BOT_DATA"], "w") as bot_data:
            json.dump(data, bot_data)

        await reply(ctx, "Done")

    @commands.Cog.listener("on_message")
    async def on_message(self, m):
        if m.author == self.bot:
            return

        if m.content.lower() in BadWords.instance.words:
            await m.delete()
            await m.author.send("You are not allowed to use inappropriate words here.")


def setup(bot: discord.Bot):
    bot.add_cog(ChannelModCog(bot))
# No hate speech / racism  Use proper names - keep names appropriate IE NO swear words in name etc.  Don’t be an asshole to other people. We are here for fun.  No spamming chat or being a big Troll  Keep Toxicity to a minimum  Respect our Admins / Moderators (They are Volunteers)  Don't cause Drama - Keep arguments private  No advertising or advertising your server. This includes self promotion.  Keep content in proper Channels.  Let people know you are Streaming (giving a heads up or asking goes a long way)  DO NOT DM members advertising your server unless asked to. (If a member DM's you inviting you to other servers please use the command ?report @<user> reason don't lie about your age - Underage members found to have selected the Over 18 role, will be warned and given the under 18 role.
