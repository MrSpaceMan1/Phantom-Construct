import json
import discord
from discord import option
from discord import SlashCommandOptionType as types
from discord.ext import commands
from legacy.utils import reply, no_premissions
from dotenv import dotenv_values

guilds_ids = [969636569206120498]
env = dotenv_values(".env")


class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close ticket",
                       custom_id=f"persistent-close-ticket",
                       style=discord.ButtonStyle.gray,
                       emoji="🔒")
    async def button_callback(self, button, interaction):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("⛔ Insufficient permissions ⛔", ephemeral=True)
            return
        thread = interaction.channel

        with open(env["THREADS"], 'r') as threads:
            data = json.load(threads)
            user = data[f"{thread.id}"]
            del data[f"{thread.id}"]

        with open(env["THREADS"], 'w') as threads_w:
            json.dump(data, threads_w)

        optional_member = interaction.guild.get_member(user)
        member = optional_member if optional_member else await interaction.guild.fetch_member(user)

        await thread.remove_user(member)
        await interaction.response.send_message("Archiving thread", ephemeral=True)
        await thread.archive(locked=True)

        with open("transcript.txt", "w") as transcript:
            transcript_string = ""
            async for message in thread.history():
                date = message.created_at
                transcript_string = f"{message.author}: {message.content}\n" + transcript_string
            transcript_string = f"{date.year}-{date.month}-{date.day} | {thread.name} \n\n" + transcript_string
            transcript.write(transcript_string)

        with open(env["BOT_DATA"], 'r') as bot_data:
            data = json.load(bot_data)
            if data.get("transcript_channel") is None:
                await interaction.response.send_message("No transcript channel set. Set transcript channel first.",
                                                        ephemeral=True)
                return

            possible_channel = interaction.guild.get_channel(data["transcript_channel"])
            channel = possible_channel if possible_channel else await interaction.guild.fetch_channel(
                data["transcript_channel"])

            if channel is None:
                await interaction.response.send_message("Channel doesn't exist")
                return

            await channel.send(file=discord.File("transcript.txt", filename=f"{thread.name}.txt"))
        return


class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open ticket",
                       custom_id="persistent-ticket",
                       style=discord.ButtonStyle.primary,
                       emoji='📄')
    async def button_callback(self, button, interaction):
        user_id = interaction.user.id

        with open(env["THREADS"], "r") as thread_ownership:
            thread_list = json.load(thread_ownership)
            owners_ids = thread_list.values()

            if user_id in owners_ids:
                await interaction.response.send_message(
                    "You already have a ticket open. Finish it before opening another one.",
                    ephemeral=True)
                return

        with open(env["THREADS"], "w") as thread_ownership:

            thread = await interaction.channel.create_thread(
                name=f"{interaction.user} - Ticket",
                auto_archive_duration=1440,
                type=discord.ChannelType.public_thread
            )
            thread_list[thread.id] = user_id
            json.dump(thread_list, thread_ownership)

        help_roles_string = ""
        with open(env["BOT_DATA"], "r") as bot_data:
            data = json.load(bot_data)
            if data.get("help_roles") is not None:
                for role in data["help_roles"]:
                    help_roles_string += f"<@&{role}> "

        await thread.add_user(interaction.user)
        await thread.send(f"Our staff will be with you shortly. When the ticket is done, staff will close the ticket. "
                          f"{help_roles_string}",
                          allowed_mentions=discord.AllowedMentions.all(),
                          view=CloseTicket())
        await interaction.response.send_message(f"Ticket created: {thread.jump_url}", ephemeral=True)
        await interaction.channel.purge(limit=1)


class ServerSupportCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot

    @commands.slash_command(name="transcript-channel",
                            description="Set the channel to send transcripts to")
    @option("channel", type=types.channel)
    async def transcript_channel(self, ctx, channel):
        if not ctx.interaction.user.guild_permissions.moderate_members:
            await no_premissions(ctx)
            return

        with open(env['BOT_DATA'], "r") as bot_data:
            data = json.load(bot_data)
            data["transcript_channel"] = channel.id

        with open(env["BOT_DATA"], "w") as bot_data:
            json.dump(data, bot_data)

        await reply(ctx, "Done")

    @commands.slash_command(name="ticket-channel",
                            description="Create ticket system in desired channel. Only one should exist")
    async def ticket_channel(self, ctx):
        if not ctx.interaction.user.guild_permissions.moderate_members:
            await no_premissions(ctx)
            return

        await ctx.interaction.response.send_message(view=CreateTicket())

    help = discord.SlashCommandGroup("help-roles", "Set helper roles")

    @help.command(description="Add helper roles")
    @option(name="role", type=types.role)
    async def add(self, ctx, role):
        if not ctx.interaction.user.guild_permissions.moderate_members:
            await no_premissions(ctx)
            return

        with open(env["BOT_DATA"], "r") as bot_data:
            data = json.load(bot_data)
            if data.get("help_roles") is None:
                data["help_roles"] = []

            if role.id in data["help_roles"]:
                await reply(ctx, "Role already on list")
                return

            data["help_roles"].append(role.id)

            with open(env["BOT_DATA"], "w") as bot_data_write:
                json.dump(data, bot_data_write)

        await reply(ctx, "Role added")

    @help.command(description="Remove helper role")
    @option(name="role", type=types.role)
    async def remove(self, ctx, role):
        if not ctx.interaction.user.guild_permissions.moderate_members:
            await no_premissions(ctx)
            return

        with open(env["BOT_DATA"], "r") as bot_data:
            data = json.load(bot_data)
            if data.get("help_roles") is None:
                await reply(ctx, "No roles in list")
                return
            data["help_roles"] = list(filter(lambda x: x != role.id, data["help_roles"]))

            with open(env["BOT_DATA"], "w") as bot_data_write:
                json.dump(data, bot_data_write)
        await reply(ctx, "Role removed")

    @help.command(description="Display helper roles")
    async def display(self, ctx):
        if not ctx.interaction.user.guild_permissions.moderate_members:
            await no_premissions(ctx)
            return
        with open(env["BOT_DATA"], "r") as bot_data:
            data = json.load(bot_data)
            if data.get("help_roles") is None:
                await reply(ctx, "No roles in list")
                return
            guild = ctx.interaction.guild
            roles = []
            for role in data["help_roles"]:
                roles.append(guild.get_role(role).name)
            await reply(ctx, roles)
            return


def setup(bot: discord.Bot):
    bot.add_cog(ServerSupportCog(bot))
