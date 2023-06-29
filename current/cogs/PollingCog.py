import uuid
import discord as d
from discord.ext import tasks
from current.utils.constants import POLL_ROLE
from current.utils.my_bot import MyBot
from current.views.Poll import Poll
import current.utils.poll_utils as poll_utils


class PollingCog(d.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot

    poll_permissions = d.Permissions()
    poll_permissions.moderate_members = True
    poll = d.SlashCommandGroup(
        name="poll",
        description="Polls related commands",
        default_member_permissions=poll_permissions
    )

    @poll.command()
    async def role(self, ctx: d.ApplicationContext, role: d.Option(d.Role, description="Role to be set")):
        """Set role for role makers"""
        self.bot.data[POLL_ROLE] = role.id
        await ctx.respond("Role set", ephemeral=True)

    @poll.command()
    async def create(
            self,
            ctx: d.ApplicationContext,
            question: d.Option(str, description="Question to ask"),
            answers: d.Option(str, description="Provide answers in a form of #answer1#answer2#... where # is division character of your choice"),
            time: d.Option(float, description="Time in hours. Fractions possible") = 0.01,
            max_choices: d.Option(int, description="Max choices") = 1
    ):
        """Create poll"""
        poll_creator_id = self.bot.data[POLL_ROLE]
        if poll_creator_id not in map(lambda x: x.id, ctx.user.roles):
            return await ctx.respond("You don't have the required role to create poll", ephemeral=True)

        seconds_to_conclude = time * 3600
        poll_id = uuid.uuid4().hex
        options = [d.SelectOption(label=o) for o in answers.split(answers[0])[1:]]
        pollHandler = poll_utils.PollHandler(poll_id, self.bot)
        pollView: Poll = Poll(pollHandler, options, poll_id, (1, max_choices))

        # pollUtils.finish_poll_task_creator(self.bot, pollView, seconds_to_conclude)
        # await ctx.respond(question, view=pollView)
        await ctx.respond(question, view=pollView)

    @tasks.loop(minutes=2.0)
    async def finalize(self):
        pass

    @finalize.before_loop
    async def b4_finalize(self):
        await self.bot.wait_until_ready()
def setup(bot: MyBot):
    bot.add_cog(PollingCog(bot))
