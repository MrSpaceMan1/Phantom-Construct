import discord
import json
from dotenv import dotenv_values
import WarningSystem
from BotData import BotData



def main():
    bot = discord.Bot(debug_guilds=[969636569206120498], intents=discord.Intents.all())
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

    try:
        with open("warnings.json", "r") as warnings_file:
            WarningSystem.setup(bot)
            warnings = json.load(warnings_file)
            bot.warning_system.warnings = warnings
    except FileNotFoundError:
        raise FileNotFoundError("Missing warnings.json file")

    extension_list = ["channel_mod", "warnings"]
    env = dotenv_values(".env")

    for extension in extension_list:
        bot.load_extension(f"cogs.{extension}")

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")
        print(bot.commands)

    bot.data = bd.data
    bot.run(env["TOKEN"])


if __name__ == "__main__":
    main()
