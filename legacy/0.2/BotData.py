import discord
import dotenv
import json

env = dotenv.dotenv_values()


class BotData:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(BotData, cls).__new__(cls)
        return cls.instance

    def __init__(self, bot):
        self.data = dict()
        self.bot = bot

    def set_no_save(self, key, value):
        self.data[key] = value

    def __setitem__(self, key, value):
        self.data[key] = value

        with open(env["BOT_DATA"], "w") as bot_data_file:
            json_string = json.dumps(self.data, indent=4)
            print(json_string, end="\n\n\n")
            bot_data_file.write(json_string)
            bot_data_file.close()

    def __getitem__(self, key):
        return self.data[key]

    @property
    def getDict(self):
        return self.data

    def get(self, key):
        return self.data.get(key)


def setup(bot: discord.Bot):
    bot.data = BotData(bot)
