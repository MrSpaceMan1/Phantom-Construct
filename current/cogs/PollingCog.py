import asyncio, math, discord, uuid
from discord import Option, Role, ApplicationContext
from current.utils.MyBot import MyBot
from current.views.Poll import Poll
from typing import List
import current.utils.pollUtils as pollUtils


class PollingCog(discord.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    poll = discord.SlashCommandGroup("poll", "Polls related commands")

    @poll.command(name="role", description="Set role for poll makers")
    async def role(self, ctx: ApplicationContext, role: Option(discord.Role, description="Role to be set")):
        perms = ctx.user.guild_permissions
        if not perms.moderate_members:
            await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)
            return

        self.bot.data["poll_role"] = role.id
        await ctx.respond("Role set", ephemeral=True)

    @poll.command(name="create", description="Create poll")
    async def create(
            self,
            ctx: ApplicationContext,
            question: Option(str, description="Question to ask"),
            answers: Option(str, description="Provide answers in a form of ;answer1;answer2;..."),
            time: Option(float, description="Time in hours. Fractions possible", required=True),
            max_choices: Option(int, description="Max choices") = 1
    ):
        poll_creator = self.bot.data["poll_role"]
        if poll_creator not in map(lambda x: x.id, ctx.user.roles):
            await ctx.respond("You don't have the required role to create poll", ephemeral=True)
            return

        seconds_to_conclude = time * 60 * 60
        poll_id = uuid.uuid4().hex
        options: List[discord.SelectOption] = list(map(lambda x: discord.SelectOption(label=x), answers.split(answers[0])[1:]))
        pollView: Poll = Poll(
            self.bot, ctx, question, poll_id, options, max_choices, "Pick your answer"
        )

        self.bot.session["poll"][poll_id] = {}

        pollUtils.finish_poll_task_creator(self.bot, pollView, seconds_to_conclude)
        await ctx.respond(question, view=pollView)


def setup(bot: MyBot):
    bot.add_cog(PollingCog(bot))
