import json
import datetime
import discord
from dotenv import dotenv_values

env = dotenv_values()


class WarningSystem:
    def __init__(self, _bot: discord.Bot):
        self.bot = _bot
        self.warnings = {}

    async def add_warning(self, user: discord.Member):
        if self.warnings.get(str(user.id)) is None:
            self.warnings[str(user.id)] = 1
        else:
            self.warnings[str(user.id)] += 1

        if self.warnings[str(user.id)] == 1:
            await user.timeout_for(datetime.timedelta(minutes=15))
            await user.send(
                "You have been issued a warning. Since this is a first offence you will be timed out for 15 minutes. "
                "Behave.")
        elif self.warnings[str(user.id)] == 2:
            await user.timeout_for(datetime.timedelta(hours=2))
            await user.send(
                "You have been issued a warning. This is your second offence. You're timed out for two hours. "
                "Behave."
            )
        elif self.warnings[str(user.id)] == 3:
            await user.timeout_for(datetime.timedelta(weeks=1))
            await user.send(
                "You have been issued a warning. This is your second offence. You're timed out for a week. "
                "This is your last warning. Next violation will result in ban. Behave."
            )
        elif self.warnings[str(user.id)] == 4:
            await user.send(
                "You have been banned from the server."
            )
            await user.ban(delete_message_days=1)

        with open(env["WARNINGS"], "w") as warnings_file:
            json.dump(self.warnings, warnings_file, indent=4)

    async def remove_warning(self, user: discord.Member):
        if self.warnings.get(str(user.id)) is None:
            self.warnings[str(user.id)] = 0
        else:
            if self.warnings[str(user.id)] > 0:
                self.warnings[str(user.id)] -= 1

        with open(env["WARNINGS"], "w") as warnings_file:
            json.dump(self.warnings, warnings_file, indent=4)


def setup(bot: discord.Bot):
    bot.warning_system = WarningSystem(bot)
