import datetime
from typing import cast
import discord as d
import thefuzz.fuzz
from discord.ext import tasks
from bot.my_bot import MyBot
from entities import Reminder
from entities.reminder_helper import from_reminder_data
from data_classes import ReminderData
from utils.iterable_methods import map_, find

def code_autocomplete(ctx: d.AutocompleteContext):
    cog = cast(RemindersCog, ctx.cog)
    keys = map_(cog.reminders, lambda x: x.id)
    sorted_keys = sorted(keys, key=lambda x: thefuzz.fuzz.ratio(x, ctx.value))
    return sorted_keys[:5]


class RemindersCog(d.Cog):
    def __init__(self, bot: MyBot):
        self.bot: MyBot = bot
        self.reminders: list[Reminder] = list()
        self.remind.start()

    reminders_perms = d.Permissions()
    reminders_perms.moderate_members = True
    reminder = d.SlashCommandGroup(
        name="reminder",
        description="reminders related commands",
        default_member_permissions=reminders_perms
    )

    @reminder.command()
    async def add(
            self,
            ctx: d.ApplicationContext,
            content: d.Option(str, description="Content of reminder"),
            channel: d.Option(d.TextChannel, "Channel to send reminder in"),
            times: d.Option(int, "If it is one time or reoccurring; Defaults to infinite") = -1,
            months: d.Option(int, "Additive frequency in months") = 0,
            days: d.Option(int, "Additive frequency in days") = 0,
            hours: d.Option(int, "Additive frequency in months") = 0,
            minutes: d.Option(int, "Additive frequency in minutes") = 0,
    ):
        """Create new reminder"""
        if not any([months, days, hours, minutes]):
            return await ctx.respond("No frequencies were set", ephemeral=True)
        channel: d.TextChannel

        reminder = Reminder(
            self.bot,
            content,
            (months, days, hours, minutes),
            channel,
            username=ctx.user.name,
            times=times
        )
        with self.bot.data.access_write() as state:
            self.reminders.append(reminder)
            state.reminders[reminder.id] = ReminderData.from_reminder(reminder)

        await ctx.respond("Reminder set", ephemeral=True)

    @reminder.command()
    async def remove(
            self,
            ctx: d.ApplicationContext,
            name: d.Option(str, "Id for reminder", autocomplete=code_autocomplete)
    ):
        """Remove existing reminder"""
        with self.bot.data.access_write() as state:
            if not state.reminders.get(name):
                return ctx.respond("Reminder with given name doesn't exist", ephemeral=True)
            index = find(self.reminders, lambda x: x.id == name)
            self.reminders.pop(index)
            del state.reminders[name]

        await ctx.respond("Reminder removed", ephemeral=True)

    @reminder.command()
    async def list(self, ctx: d.ApplicationContext):
        """Lists all existing reminders """
        reminders_list_str = ""
        for reminder in self.reminders:
            content = reminder.content if len(reminder.content) < 15 else reminder.content[:15]+"..."
            reminders_list_str += f"'{reminder.id}': {content}\n"

        if not reminders_list_str:
            reminders_list_str = "There aren't any reminders\n"
        await ctx.respond(reminders_list_str[:-1], ephemeral=True)

    async def load_reminders(self):

        with self.bot.data.access() as state:
            for rem_id, rem_data in state.reminders.items():
                self.reminders.append(await from_reminder_data(rem_id, rem_data))

    @tasks.loop(minutes=1)
    async def remind(self):
        now = datetime.datetime.now().timestamp()
        next_reminders = []
        del_reminders = []
        for reminder in self.reminders:
            if now >= reminder.next_timestamp:
                try:
                    await reminder.channel.send(content=reminder.content)
                    reminder.set_next_timestamp()
                    if reminder.times > 0:
                        reminder.decrement_times()

                    if reminder.times != 0:
                        next_reminders.append(reminder)
                    else:
                        del_reminders.append(reminder)
                except d.HTTPException:
                    print("Couldn't send reminder, trying again in a minute")
            else:
                next_reminders.append(reminder)

        with self.bot.data.access_write() as state:
            for reminder in del_reminders:
                del state.reminders[reminder.id]
        self.reminders = next_reminders

    @remind.before_loop
    async def wait_for_ready(self):
        await self.bot.wait_until_ready()
        await self.load_reminders()


def setup(bot: MyBot):
    bot.add_cog(RemindersCog(bot))
