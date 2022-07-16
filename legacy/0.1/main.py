import json
import discord
from dotenv import dotenv_values
from cogs.server_support import CreateTicket, CloseTicket
from utils import BadWords

env = dotenv_values(".env")
bad_words = []

bot = discord.Bot(debug_guilds=[969636569206120498], intents=discord.Intents.all())

bot.load_extension("cogs.permissions")
bot.load_extension("cogs.channel_mod")
bot.load_extension("cogs.user_mod")
bot.load_extension("cogs.server_support")

with open(env["BOT_DATA"], "r") as bot_data:
    data = json.load(bot_data)
    bw = BadWords()
    if data.get("bad_words") is not None:
        bw.words = data["bad_words"]


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    bot.add_view(CreateTicket())
    bot.add_view(CloseTicket())
    print(bot.commands)


bot.run(env["TOKEN"])  # run the bot with the token
