import datetime
import json
from enum import Enum
from typing import TextIO, Optional
import discord, discord.errors
import dotenv
import constants

env = dotenv.dotenv_values()


async def time_out(user, message, time: datetime.timedelta):
    await user.send(message)
    await user.timeout_for(time)


async def kick(user, message):
    await user.send(message)
    await user.kick()


async def ban(user, message):
    await user.send(message)
    await user.ban()


class WarningLevel:
    def __init__(self, action, message, **kwargs):
        self.action: DisciplinaryActions = action
        self.message = message
        self.params = kwargs

    async def __call__(self, user):
        try:
            await self.action(user, self.message, **self.params)
        except discord.Forbidden:
            print("Tried to moderate user with greater privileges")


class DisciplinaryActions(Enum):
    TIMEOUT = time_out
    KICK = kick
    BAN = ban


class WarningSystem:
    def __init__(self, bot):
        self.bot = bot
        self.__warning = {}
        self.__levels = []

    def __getitem__(self, key):
        return self.__warning.get(key)

    def __setitem__(self, key: str, value: int):
        self.__warning[key] = value
        json_string = json.dumps(self.__warning, indent=4)

        with open(env["WARNINGS"], "w", encoding="utf-8") as warnings_file:
            warnings_file.write(json_string)

    async def issue(self, user, guild):
        if guild is None:
            raise discord.errors.Forbidden
        super_member = user.guild_permissions.is_superset(guild.me.guild_permissions)
        if super_member:
            return

        with self.bot.data.access() as state:
            log_channel_id = state.warning_log_channel

        log_channel = await self.bot.get_or_fetch_channel(log_channel_id)
        warnings_count = self[user.id] or 0

        if warnings_count + 1 <= len(self.__levels):
            await self.__levels[warnings_count](user)
            self[str(user.id)] = warnings_count + 1

            if log_channel:
                avatar = user.avatar or user.default_avatar
                warning = discord.Embed(title="Warning issued") \
                    .set_author(name=f"@{user.name}", icon_url=avatar.url)
                warning.colour = discord.Colour.orange()

                await log_channel.send(embed=warning)

            return

        if log_channel:
            await log_channel.send(f"User @{user.name} "
                                   "reached max amount of warnings")

    async def retract(self, user):
        with self.bot.data.access() as state:
            log_channel_id = state.warning_log_channel
        log_channel = await self.bot.get_or_fetch_channel(log_channel_id)

        warnings_count = self[str(user.id)] or 0
        warnings_count = warnings_count - 1 if warnings_count > 0 else 0

        self[str(user.id)] = warnings_count

        if log_channel:
            avatar = user.avatar or user.default_avatar
            warning = discord.Embed(title="Warning retracted", description="Any penalties that haven't expired yet"
                                                                           " have to be removed manually") \
                .set_author(name=f"@{user.name}", icon_url=avatar.url)
            warning.colour = discord.Colour.green()

            await log_channel.send(embed=warning)

    def load(self, file):
        json_dict = json.loads(file.read())
        self.__warning = json_dict

    def add_action(self, action, message = "", **kwargs):
        self.__levels.append(WarningLevel(action, message, **kwargs))

    @property
    def warnings(self):
        return self.__warning

    def __call__(self):
        return self.warnings
