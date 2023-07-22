import string
from datetime import datetime, timedelta
from typing import Type
import discord as d
from monthdelta import monthdelta
from utils import MyBot
from utils.constants import *


class Reminder:
    CONTENT = "content"
    DELAY = "delay"
    NEXT_TIMESTAMP = "next"
    CHANNEL_ID = "channel_id"
    TIMES = "times"
    ID = "id"

    def __init__(
            self,
            bot: MyBot,
            content: str,
            delay: list[int, int, int, int],
            channel: d.TextChannel,
            username: str = None,
            times: int = -1,
            id: str = None,
            next_timestamp: float = None
    ):
        self.bot = bot
        self.content = content
        self.delay = delay
        self.username = username
        self.id = id if id else reminder_codename_gen(self)
        self.next_timestamp: float
        self.channel = channel
        self.times = times

        if not next_timestamp:
            now = datetime.now()
            [months, days, hours, minutes] = delay
            self.next_timestamp: datetime = now + monthdelta(months) + timedelta(days=days, hours=hours,
                                                                                 minutes=minutes)
            self.next_timestamp = self.next_timestamp.timestamp()
        else:
            self.next_timestamp = next_timestamp

        if not id:
            reminders = self.bot.data.get(REMINDERS) or dict()

            reminders[self.id] = {
                Reminder.CONTENT: content,
                Reminder.DELAY: delay,
                Reminder.NEXT_TIMESTAMP: self.next_timestamp,
                Reminder.TIMES: times,
                Reminder.CHANNEL_ID: channel.id
            }
            self.bot.data[REMINDERS] = reminders

    def set_next_timestamp(self):
        [months, days, hours, minutes] = self.delay
        self.next_timestamp: datetime = datetime.now() + monthdelta(months) + timedelta(days=days, hours=hours,
                                                                                        minutes=minutes)
        self.next_timestamp = self.next_timestamp.timestamp()

        reminders = self.bot.data.get(REMINDERS) or dict()
        this = reminders[self.id]
        this[Reminder.NEXT_TIMESTAMP] = self.next_timestamp
        reminders[self.id] = this
        self.bot.data[REMINDERS] = reminders

    def decrement_times(self):
        self.times -= 1

        reminders = self.bot.data.get(REMINDERS) or dict()
        this = reminders[self.id]
        this[Reminder.TIMES] = self.times
        reminders[self.id] = this
        self.bot.data[REMINDERS] = reminders

    def __str__(self):
        return f"Reminder(" \
               f"id={self.id}, " \
               f"content={self.content}, " \
               f"next_timestamp={self.next_timestamp}, " \
               f"channel={self.channel}, " \
               f"times={self.times})"


def reminder_codename_gen(rem: Reminder):
    name = rem.username
    stop_chars = string.punctuation + string.whitespace
    trans_table = str.maketrans(stop_chars, len(stop_chars) * " ")
    clean = rem.content.translate(trans_table).replace(" ", "")
    code = clean[:4] + clean[-4:]

    reminders = rem.bot.data.get(REMINDERS) or dict()
    num = ""

    while True:
        code_name = ":".join([name, code]) + str(num)
        if not reminders.get(code_name):
            return code_name
        num = 1 if not num else num + 1
