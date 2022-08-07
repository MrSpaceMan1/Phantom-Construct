import discord
from discord import ApplicationContext, Option
from current.utils.MyBot import MyBot


class DynamicVoiceChatCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    vc = discord.SlashCommandGroup("auto-vc", "Ground of commands to set dynamic voice channels")

    @vc.command(name="set-trigger-channel", description="Set the channel that will trigger channel creation")
    async def set_trigger_channel(
            self,
            ctx: ApplicationContext,
            channel: Option(discord.VoiceChannel, description="Channel to set")
    ):
        perms = ctx.user.guild_permissions
        if not perms.moderate_members:
            await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)
            return

        self.bot.data["autovc_channel"] = int(channel.id)
        await ctx.respond("Channel set", ephememral=True)


def setup(bot: MyBot):
    bot.add_cog(DynamicVoiceChatCog(bot))
