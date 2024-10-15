import uuid
import my_bot


class Poll:
    def __init__(
            self,
            bot: my_bot.MyBot,
            answers: list[str],
            choices: list[int, int],
            timestamp: float,
            votes: dict[int, list[str]] = None,
            poll_id=None,
            message=None
    ):
        self.poll_id = uuid.uuid4().hex if poll_id is None else poll_id
        self.bot = bot
        self.answers = answers
        self.choices = choices
        self.timestamp = timestamp
        self.votes = dict() if votes is None else votes

        self.handler = utils.polls.PollHandler(self)
        if message:
            self.handler.set_message(message)
        self.view = PollView(self)
