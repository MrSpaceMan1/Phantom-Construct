from current.utils.constants import POLL
from current.utils.my_bot import MyBot

number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣",
                 "🔟", "1️⃣1️⃣", "1️⃣2️", "1️2️", "1️3️"]


class PollHandler:
    VOTES = "votes"
    FINISH = "finish"
    def __init__(self,
                 poll_id: str,
                 bot: MyBot,
                 ):
        self.bot = bot
        self.id = poll_id
        self.finished = False

        polls = self.bot.data[POLL]
        polls[poll_id] = {
            PollHandler.FINISH: 1,
            PollHandler.VOTES: dict()
        }
        self.bot.data[POLL] = polls

    class PollException(Exception):
        def __init__(self, message):
            super().__init__(message)
    def set_votes(self, user_id: int, values: list[str]) -> None:
        if self.finished:
            raise self.PollException("Poll has finished")

        polls = self.bot.data.get(POLL)
        this_poll = polls.get(self.id)
        this_poll[PollHandler.VOTES][user_id] = values
        polls[self.id] = this_poll
        self.bot.data[POLL] = polls

    def get_results(self) -> dict[str, int]:
        if self.finished:
            raise self.PollException("Poll has finished")

        polls = self.bot.data.get(POLL)
        votes: dict[int, list[str]] = polls.get(self.id).get(PollHandler.VOTES)
        results: dict = dict()
        for choices in votes.values():
            for choice in choices:
                results[choice] = results.get(choice) + 1 if results.get(choice) else 1
        for key in results.keys():
            results[key] = str(results[key])
        return results

    def finish_poll(self) -> None:
        if self.finished:
            raise self.PollException("Poll has finished")

        polls: dict[str, dict] = self.bot.data[POLL]
        polls.pop(self.id)
        self.bot.data[POLL] = polls
        self.finished = True

