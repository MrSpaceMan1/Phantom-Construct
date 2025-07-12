from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from monthdelta import monthdelta
from data_classes import ReminderData
from .reminder_helper import reminder_codename_gen

if TYPE_CHECKING:
    from bot.my_bot import MyBot


class Reminder:
    CONTENT = "content"
    DELAY = "delay"
    NEXT_TIMESTAMP = "next"
    CHANNEL_ID = "channel_id"
    TIMES = "times"
    ID = "id"

    def __init__(
            self,
            bot: "MyBot",
            content: str,
            delay: tuple[int, int, int, int],
            channel: int,
            username: str = None,
            times: int = -1,
            id_: str = None,
            next_timestamp: float = None
    ):
        self.bot = bot
        self.content = content
        self.delay = delay
        self.username = username
        self.id = id_ if id_ else reminder_codename_gen(self)
        self.next_timestamp: float
        self.channel = channel
        self.times = times

        if not next_timestamp:
            now = datetime.now()
            (months, days, hours, minutes) = delay
            self.next_timestamp: float = (
                now + monthdelta(months) + timedelta(days=days, hours=hours, minutes=minutes)) \
                .replace(second=0, microsecond=0)\
                .timestamp()
        else:
            self.next_timestamp = next_timestamp

        if not id_:
            with self.bot.data.access_write() as write_state:
                write_state.reminders[self.id] = ReminderData(
                    content=content,
                    delay=delay,
                    next=self.next_timestamp,
                    times=times,
                    channel_id=channel.id
                )

    def set_next_timestamp(self) -> None:
        (months, days, hours, minutes) = self.delay
        self.next_timestamp: float = (
            datetime.now() + monthdelta(months) + timedelta(days=days, hours=hours, minutes=minutes))\
            .replace(second=0, microsecond=0)\
            .timestamp()

        with self.bot.data.access_write() as write_state:
            write_state.reminders[self.id].next = self.next_timestamp

    def decrement_times(self) -> None:
        self.times -= 1
        with self.bot.data.access_write() as write_state:
            write_state.reminders[self.id].times = self.times

    def __str__(self):
        return f"Reminder(" \
               f"id={self.id}, " \
               f"content={self.content}, " \
               f"next_timestamp={self.next_timestamp}, " \
               f"channel={self.channel}, " \
               f"times={self.times})"