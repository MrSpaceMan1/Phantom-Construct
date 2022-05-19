import discord
from discord.ext import commands
from discord import option, SlashCommandOptionType as Types


class ChannelModCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.slash_command(name="move-messages", description="Move messages to another channel")
    @option(name="amount", type=Types.number, description="Number of messages to move")
    @option(name="channel", type=Types.channel, descripion="Channel to move messages to")
    @commands.has_permissions(manage_messages=True)
    async def move_messages(self, ctx, amount, channel):
        if type(channel) != discord.TextChannel:
            await ctx.respond("Provided channel is not a text channel", ephemeral=True)
            return
        if amount < 1:
            await ctx.respond("Cannot move less then 1 message", ephemeral=True)
            return
        amount = int(amount)

        await ctx.respond("Nothing", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(ChannelModCog(bot))
