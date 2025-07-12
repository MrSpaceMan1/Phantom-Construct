import typing
import string

import discord

from bot.my_bot import MyBot
from . import reminder

if typing.TYPE_CHECKING:
    from entities import Reminder
    from data_classes import ReminderData

async def from_reminder_data(rem_id: str, rem: "ReminderData") -> "Reminder":
    bot_ = MyBot.get_instance()
    channel = typing.cast(discord.TextChannel, await bot_.get_or_fetch_channel(rem.channel_id))
    if not channel:
        raise ValueError(f"Channel with id {rem.channel_id} doesn't exist")

    return reminder.Reminder(
        bot=bot_,
        content=rem.content,
        delay=rem.delay,
        channel=channel,
        username=rem.username,
        times=rem.times,
        id_=rem_id,
        next_timestamp=rem.next
    )

def reminder_codename_gen(rem: "Reminder"):
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