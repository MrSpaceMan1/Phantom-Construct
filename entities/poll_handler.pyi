from typing import Optional
import discord
from my_bot import MyBot
from poll import Poll


class PollHandler:
    VOTES = "votes"
    FINISH = "finish"
    MESSAGE_ID = "msg_id"
    CHANNEL_ID = "channel_id"
    GUILD_ID = "guild_id"
    ANSWERS = "answer"
    CHOICES = "choices"
    EMOJIS = "emojis"
    def __init__(self, poll: Poll):
        self.poll: Poll = poll
        self.bot: MyBot = poll.bot
        self.id: str = poll.poll_id
        self.message: Optional[discord.Message] = None
        self.finished: bool = False

    class PollException(Exception):
        def __init__(self, message: str):...

    def set_message(self, message: discord.Message) -> None:...
    def set_votes(self, user_id: int, values: list[str]) -> None:...
    def get_results(self) -> dict[str, int]:...
    async def finish_poll(self) -> None:...
    def delete_poll(self) -> None:...