import asyncio
import discord
import json
from BotData import BotData
from dotenv import dotenv_values


def prepare():
    bd = BotData()

    try:
        with open(".env", 'r'):
            pass
    except FileNotFoundError:
        raise FileNotFoundError("Missing .env file")

    try:
        with open("bot_data.json", "r") as bot_data_file:
            bot_data = json.load(bot_data_file)
            for key in bot_data.keys():
                bd[key] = bot_data[key]
    except FileNotFoundError:
        raise FileNotFoundError("Missing bot_data.json file")

    main()


def main():
    bot = discord.Bot(bot=discord.Bot(debug_guilds=[969636569206120498], intents=discord.Intents.all()))
    extension_list = ["channel_mod"]
    env = dotenv_values(".env")

    for extension in extension_list:
        bot.load_extension(f"cogs.{extension}")

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")
        print(bot.commands)
    bot.run(env["TOKEN"])


if __name__ == "__main__":
    prepare()
