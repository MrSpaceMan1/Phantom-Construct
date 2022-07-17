import discord
from discord.ext import commands
from discord import Option


class MessageModCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="move-messages", description="Move {n} messages to another channel")
    async def move_messages(
            self,
            ctx: discord.ApplicationContext,
            amount: Option(int, description="Number of messages to move"),
            channel: Option(discord.TextChannel, description="Channel to move messages to")
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
            content = message.content
            embeds = message.embeds

            if not content and not embeds:
                await message.delete()
                continue

            await webhook.send(
                content=content,
                embeds=embeds,
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

            all_msg, usr_msg = 0, 0
            async for message in channel.history(limit=100):
                if is_user(message):
                    usr_msg += 1
                all_msg += 1
                if usr_msg == number:
                    break

            messages_deleted = len(await channel.purge(limit=number, check=is_user))

        else:
            messages_deleted = len(await channel.purge(limit=number))

        await ctx.respond(f"Deleted {messages_deleted} messages", ephemeral=True)

    @commands.slash_command(name="format", description="Formatting cheatsheet")
    async def format(self, ctx: discord.ApplicationContext):
        await ctx.respond(
            """Discord has implemented a subset of markdown for text formatting. Most of these can be combined. For example: __~~***`UnderlineStrikethroughBoldItalicCode`***~~__ = UnderlineStrikethroughBoldItalicCode

TIP: In order to make the formatting not render, put a \ before (and after if applicable) the formatting. For example: \**italic\** = *italic*

NB: Formatting does not work inside codeblocks or inline codeblocks. All formatting will have to be done outside, i.e., the backticks have to be the thing closest to the text. 
            """, ephemeral=True)


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

        await ctx.respond("Done", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(MessageModCog(bot))
