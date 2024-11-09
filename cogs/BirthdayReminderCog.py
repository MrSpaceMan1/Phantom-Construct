import datetime
import typing
from datetime import date
import discord as d
from discord import HTTPException, TextChannel
from discord.ext import commands, tasks
from bot.my_bot import MyBot
from data_classes.birthday_data import BirthdayData
from utils.iterable_methods import find


def THIS_YEAR() -> int:
    return date.today().year

class BirthdayReminderCog(d.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot
        self.check_birthdays.start()

    birthday_perms = d.Permissions()
    birthday_perms.manage_messages = True
    birthday = d.SlashCommandGroup(
        name="birthdays",
        description="birthday related commands",
        default_member_permissions=birthday_perms
    )

    @birthday.command()
    async def set_channel(self,
                           ctx: d.ApplicationContext,
                           channel: d.Option(d.SlashCommandOptionType.channel, description="Where to send announcements")):
        channel: d.abc.GuildChannel
        if channel and channel.type == d.ChannelType.text:
            with self.bot.data.access_write() as write_state:
                write_state.birthday_channel_id = channel.id
            return await ctx.response.send_message("Channel set", ephemeral=True)
        await ctx.response.send_message("Channel either empty or not a text channel", ephemeral=True)


    @birthday.command()
    async def set(
            self,
            ctx: d.ApplicationContext,
            month: d.Option(int, description="month of birthday"),
            day: d.Option(int, description="day of birthday"),
            member: d.Option(d.Member, description="Who is the birthday boy/girl/person?")
    ):
        member: d.Member
        try:
            birthdate = date(THIS_YEAR(), month, day)
            if birthdate > date.today():
                next_trigger_year = THIS_YEAR()
            else:
                next_trigger_year = THIS_YEAR() + 1

            response_message: str
            with self.bot.data.access_write() as write_state:
                index_ = find(write_state.birthdays, lambda x: x.member_id == member.id)
                if index_ >= 0:
                    write_state.birthdays[index_] = BirthdayData(member_id=member.id, date=(month, day), next_trigger_year=next_trigger_year)
                    response_message = f"Birthday for member {member.display_name} saved."
                else:
                    write_state.birthdays.append(BirthdayData(member_id=member.id, date=(month, day), next_trigger_year=next_trigger_year))
                    response_message = f"Birthday for member {member.display_name} has been updated."

            await ctx.response.send_message(response_message, ephemeral=True)

        except ValueError as e:
            await ctx.response.send_message(str(e).capitalize(), ephemeral=True)

    @birthday.command()
    async def remove(self,
                              ctx: d.ApplicationContext,
                              member: d.Option(d.Member, description="Member whose birthday to delete")):
        member: d.Member
        with self.bot.data.access_write() as write_state:
            index_ = find(write_state.birthdays, lambda x: x.member_id == member.id)
            if index_ == -1:
                return await ctx.response.send_message("This member doesn't have a set birthday.", ephemeral=True)
            write_state.birthdays.pop(index_)
        await ctx.response.send_message(f"Birthday removed for user <@{member.id}>", ephemeral=True)

    @tasks.loop(hours=1, reconnect=True)
    async def check_birthdays(self):
        birthdays_to_announce = []
        with self.bot.data.access() as state:
            if not state.birthday_channel_id:
                return

            for birthday in state.birthdays:
                if datetime.date.today() >= birthday.get_date():
                        birthdays_to_announce.append(birthday)
        if len(birthdays_to_announce) > 0:
            with self.bot.data.access_write() as write_state:
                birthday_channel = await self.bot.get_or_fetch_channel(write_state.birthday_channel_id)
                if birthday_channel.type is d.TextChannel:
                    birthday_channel = typing.cast(d.TextChannel, birthday_channel)
                for birthday in birthdays_to_announce:
                    try:
                        await birthday_channel.send(f"Today ({birthday.date[0]}.{birthday.date[1]}) "
                                                    f"is <@{birthday.member_id}>'s birthday!")
                        index_ = find(write_state.birthdays, lambda x: x.member_id == birthday.member_id)
                        write_state.birthdays[index_].next_trigger_year += 1
                    except HTTPException:
                        print(f"Couldn't send message in channel {birthday_channel.id}")


def setup(bot: MyBot):
    bot.add_cog(BirthdayReminderCog(bot))
