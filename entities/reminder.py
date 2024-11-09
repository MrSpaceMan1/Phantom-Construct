import string
from datetime import datetime, timedelta
from monthdelta import monthdelta
import bot.my_bot
import data_classes.reminder_data


class Reminder:
    CONTENT = "content"
    DELAY = "delay"
    NEXT_TIMESTAMP = "next"
    CHANNEL_ID = "channel_id"
    TIMES = "times"
    ID = "id"

    def __init__(
            self,
            bot,
            content,
            delay,
            channel,
            username= None,
            times = -1,
            id_ = None,
            next_timestamp = None
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
                write_state.reminders[self.id] = data_classes.reminder_data.ReminderData(
                    content=content,
                    delay=delay,
                    next=self.next_timestamp,
                    times=times,
                    channel_id=channel.id
                )

    def set_next_timestamp(self):
        (months, days, hours, minutes) = self.delay
        self.next_timestamp: float = (
            datetime.now() + monthdelta(months) + timedelta(days=days, hours=hours, minutes=minutes))\
            .replace(second=0, microsecond=0)\
            .timestamp()

        with self.bot.data.access_write() as write_state:
            write_state.reminders[self.id].next = self.next_timestamp

    def decrement_times(self):
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


async def from_reminder_data(rem_id, rem):
    bot_ = bot.my_bot.MyBot.get_instance()
    channel = await  bot_.get_or_fetch_channel(rem.channel_id)
    if not channel:
        raise ValueError(f"Channel with id {rem.channel_id} doesn't exist")

    return Reminder(
        bot=bot_,
        content=rem.content,
        delay=rem.delay,
        channel=channel,
        times=rem.times,
        id_=rem_id,
        next_timestamp=rem.next
    )

def reminder_codename_gen(rem: Reminder):
    name = rem.username
    stop_chars = string.punctuation + string.whitespace
    trans_table = str.maketrans(stop_chars, len(stop_chars) * " ")
    clean = rem.content.translate(trans_table).replace(" ", "")
    code = clean[:4] + clean[-4:]
    num = ""
    with rem.bot.data.access() as state:
        while True:
            code_name = ":".join([name, code]) + str(num)
            if not state.reminders.get(code_name):
                return code_name
            num = 1 if not num else num + 1