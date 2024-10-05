import datetime
import typing
from io import FileIO
from pathlib import Path
import discord, dotenv
from constants import BOT_DATA
from bot.my_bot import MyBot
from bot.warning_system import DisciplinaryActions

env = dotenv.dotenv_values(".env")
extension_list = [
    # "MessageModCog",
    # "LoggerCog",
    # "WarningCog",
    # "MessageFilteringCog",
    # "PollingCog",
    "DynamicVoiceChatCog",
    # "RemindersCog",
    # "BirthdayReminderCog"
]

def setup():
    bot = MyBot(debug_guilds=[969636569206120498], intents=discord.Intents.all())

    try:
        with Path(env[BOT_DATA] or "").open("r") as bot_data_file:
            bot.data.init(typing.cast(FileIO, bot_data_file))
        with Path(env["WARNINGS"] or "").open() as warnings_file:
            bot.warnings.load(warnings_file)

    except FileNotFoundError:
        raise FileNotFoundError("Missing files")

    except KeyError:
        raise KeyError("Environmental variable not found")

    bot.warnings.add_action(DisciplinaryActions.TIMEOUT, "This is your first offence. You have been timed out for"
                                                         " 1 minute", time=datetime.timedelta(minutes=1))
    return
    main(bot)


def main(bot):
    for extension in extension_list:
        bot.load_extension(f"cogs.{extension}", package="current", store=False)

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")
        for cog in bot.cogs.keys():
            print(cog)
        print()

        for command in bot.commands:
            print(command)
        print()
    @bot.event
    async def on_disconnect():
        print(f"{bot.user} has disconnected from discord")

    @bot.event
    async def on_connected():
        print(f"{bot.user} has connected from discord")

    @bot.event
    async def on_resume():
        print(f"{bot.user} has resumed session")

    bot.run(env["TOKEN"])


if __name__ == "__main__":
    setup()
