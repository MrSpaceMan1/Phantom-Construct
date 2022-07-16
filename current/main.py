import discord, dotenv
from utils.MyBot import MyBot as Bot

env = dotenv.dotenv_values(".env")
extension_list = [
    "MessageModCog",
    "LoggerCog",
    # "logger",
    # "user_mod"
]


def setup():
    bot = Bot(debug_guilds=[969636569206120498], intents=discord.Intents.all())
    try:
        with open(env["BOT_DATA"], "r") as bot_data_file:
            bot.data.load(bot_data_file)

    except FileNotFoundError:
        raise FileNotFoundError("Missing config")

    except KeyError:
        raise KeyError("Environmental variable not found")

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
