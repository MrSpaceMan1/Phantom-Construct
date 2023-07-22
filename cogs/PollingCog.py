from datetime import datetime, timedelta
from typing import List
from discord.ext import tasks
import utils.auxilary_classes.poll_utils as poll_utils
from utils import *
from utils.constants import POLL_ROLE
from utils.iterable_methods import map as _map


class PollingCog(d.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot
        self.polls: List[Poll] = []
        self.finalize.start()

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
            answers: d.Option(str, description="Provide answers in a form of #answer1#answer2#... where # "
                                               "is division character of your choice"),
            time: d.Option(float, description="Time in hours. Fractions possible") = 0.01,
            min_choices: d.Option(int, min_value=1, description="Minimum number of choices") = 1,
            max_choices: d.Option(int, max_value=25, description="Max choices") = 1
    ):
        """Create poll"""
        poll_creator_id = self.bot.data[POLL_ROLE]
        if poll_creator_id not in _map(ctx.user.roles, lambda x: x.id):
            return await ctx.respond("You don't have the required role to create poll", ephemeral=True)

        if min_choices > max_choices:
            return await ctx.respond("Minimum number of choices can't be grater the the max", ephemeral=True)

        answers_str = answers.split(answers[0])[1:]
        if answers_str[-1] == "":
            answers_str = answers_str[:-1]

        seconds_to_conclude = time * 3600
        finish_time = datetime.now() + timedelta(seconds=seconds_to_conclude)

        poll = poll_utils.Poll(
            bot=self.bot,
            answers=answers_str,
            choices=[min_choices, min(len(answers_str), max_choices)],
            timestamp=finish_time.timestamp(),
        )

        if poll:
            resp = await ctx.respond(f"# {question}", view=poll.view)
            msg = await resp.original_response()
            poll.handler.set_message(msg)
            self.polls.append(poll)
        else:
            await ctx.respond("There was a problem with your poll", ephemeral=True)

    async def resend_poll_views(self):
        polls: list[Poll] = self.polls
        if not len(polls):
            saved_polls = self.bot.data[POLL]
            polls = [
                Poll(
                    self.bot,
                    answers=v[PollHandler.ANSWERS],
                    choices=v[PollHandler.CHOICES],
                    timestamp=v[PollHandler.FINISH],
                    votes=v[PollHandler.VOTES],
                    poll_id=id,
                    message=(await self.bot.get_or_fetch_message(v.get(PollHandler.CHANNEL_ID),
                                                                 v.get(PollHandler.MESSAGE_ID)))
                ) for id, v in saved_polls.items()
            ]

        for poll in polls:
            msg = poll.handler.message
            await msg.edit(view=poll.view)

    @d.Cog.listener("on_connected")
    async def on_reconnect_resend_polls(self):
        await self.resend_poll_views()

    @d.Cog.listener("on_ready")
    async def on_ready_resend_polls(self):
        await self.resend_poll_views()

    @d.Cog.listener("on_resume")
    async def on_resume_resend_polls(self):
        await self.resend_poll_views()

    @tasks.loop(minutes=1)
    async def finalize(self):
        now = datetime.now().timestamp()
        next_polls = []
        for poll in self.polls:
            if poll.timestamp < now:
                try:
                    await poll.handler.finish_poll()
                except d.HTTPException:
                    next_polls.append(poll)
            else:
                next_polls.append(poll)
        self.polls = next_polls

    @finalize.before_loop
    async def b4_finalize(self):
        await self.bot.wait_until_ready()


def setup(bot: MyBot):
    bot.add_cog(PollingCog(bot))
