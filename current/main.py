import datetime
import logging
import discord, dotenv
from utils.MyBot import MyBot as Bot
from utils.WarningSystem import DisciplinaryActions

env = dotenv.dotenv_values(".env")
extension_list = [
    "MessageModCog",
    "LoggerCog",
    "WarningCog",
    "MessageFilteringCog"
]


def setup():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='logfile.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    bot = Bot(debug_guilds=[969636569206120498], intents=discord.Intents.all(), logger=logger)

    try:
        with open(env["BOT_DATA"], "r") as bot_data_file:
            bot.data.load(bot_data_file)
        with open(env["WARNINGS"], "r") as warnings_file:
            bot.warnings.load(warnings_file)

    except FileNotFoundError:
        raise FileNotFoundError("Missing files")

    except KeyError:
        raise KeyError("Environmental variable not found")

    bot.warnings.add_action(DisciplinaryActions.TIMEOUT, "This is your first offence. You have been timed out for"
                                                         " 1 minute", time=datetime.timedelta(minutes=1))

    main(bot)


def main(bot):
    for extension in extension_list:
        bot.load_extension(f"cogs.{extension}")

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")
        for command in bot.commands:
            print(command)

    bot.run(env["TOKEN"])


if __name__ == "__main__":
    setup()
