import discord as d
from constants import *

class PollHandler:
    VOTES = "votes"
    FINISH = "finish"
    MESSAGE_ID = "msg_id"
    CHANNEL_ID = "channel_id"
    GUILD_ID = "guild_id"
    ANSWERS = "answer"
    CHOICES = "choices"
    EMOJIS = "emojis"

    def __init__(self, poll):
        self.poll = poll
        self.bot = poll.bot
        self.id = poll.poll_id
        self.message = None
        self.finished = False

        polls: dict[str, dict] = self.bot.data.get(POLL) or dict()
        polls[self.id] = {
            PollHandler.FINISH: poll.timestamp,
            PollHandler.VOTES: poll.votes,
            PollHandler.ANSWERS: poll.answers,
            PollHandler.CHOICES: poll.choices,
        }
        self.bot.data[POLL] = polls

    class PollException(Exception):
        def __init__(self, message):
            super().__init__(message)

    def set_message(self, message):
        polls = self.bot.data[POLL]
        polls[self.id][PollHandler.MESSAGE_ID] = message.id
        polls[self.id][PollHandler.CHANNEL_ID] = message.channel.id
        polls[self.id][PollHandler.GUILD_ID] = message.guild.id
        self.bot.data[POLL] = polls
        self.message = message

    def set_votes(self, user_id, values):
        if self.finished:
            raise self.PollException("Poll has finished")

        polls = self.bot.data.get(POLL)
        this_poll = polls.get(self.id)
        this_poll[PollHandler.VOTES][str(user_id)] = values
        polls[self.id] = this_poll
        self.bot.data[POLL] = polls

    def get_results(self):
        if self.finished:
            raise self.PollException("Poll has finished")

        polls = self.bot.data.get(POLL)
        poll = polls[self.id]
        votes: dict[int, list[str]] = poll[PollHandler.VOTES]
        results: dict = {key: 0 for key in self.poll.answers}
        for choices in votes.values():
            for choice in choices:
                results[choice] = results.get(choice) + 1 if results.get(choice) else 1
        for key in results.keys():
            results[key] = str(results[key])
        return results

    async def finish_poll(self):
        if self.finished:
            raise self.PollException("Poll has finished")

        results = self.get_results()
        total_votes = sum(map(int, results.values()))

        title = self.poll.handler.message.content
        embed = d.Embed()
        if total_votes and total_votes > 0:
            results_str = "\n".join(
                map(lambda x: "{0}: {1:<3} ({2:.1f}%)".format(*x, int(x[1]) / total_votes * 100), results.items())
            )
            embed.add_field(name="Results: ", value=results_str)

            await self.message.edit(content=title, view=None, embed=embed)
        else:
            embed.add_field(name="Nobody voted :(", value="")

            await self.message.edit(content=title, view=None, embed=embed)

        polls = self.bot.data[POLL]
        del polls[self.id]
        self.bot.data[POLL] = polls

    def delete_poll(self):
        """Quietly delete poll"""

        polls = self.bot.data[POLL]
        del polls[self.id]
        self.bot.data[POLL] = polls
