from operator import attrgetter
from typing import TYPE_CHECKING

from discord.ui import View, Button
from discord import Message, ButtonStyle, Interaction, InteractionResponse
from entities.autovc import AutoVC
from views.AutoVcRenameModal import AutoVcRenameModalView

if TYPE_CHECKING:
    from bot.my_bot import MyBot

class AutoVcControlMixin(View):
    def __init__(self, *items, bot: "MyBot", **kwargs):
        super().__init__(*items, **kwargs)
        self.bot = bot

    async def update_msg(self, msg: Message):
        with self.bot.data.access() as state:
            self.clear_items()
            channel_data = state.autovc_list.get(str(msg.channel.id))
            if not channel_data:
                return

            if channel_data.locked:
                view = AutoVcControlUnlockedView(self.bot)
            else:
                view = AutoVcControlView(self.bot)
        await msg.edit(view=view)

    def is_owner(self, interaction: Interaction):
        f = attrgetter("channel.id")
        channel_id = f(interaction)
        f = attrgetter("user.id")
        user_id = f(interaction)

        if not (user_id and channel_id):
            return False

        with self.bot.data.access() as state:
            autovc = state.autovc_list.get(str(channel_id), None)
            if autovc:
                return autovc.owner_id == user_id
        return False

class AutoVcControlView(AutoVcControlMixin):
    def __init__(self, bot: "MyBot"):
        super().__init__(LockChannelButton(), OpenRenameModalButton(), bot=bot, timeout=None)

class AutoVcControlUnlockedView(AutoVcControlMixin):
    def __init__(self, bot: "MyBot"):
        super().__init__(UnlockChannelButton(), OpenRenameModalButton(), bot=bot, timeout=None)


class LockChannelButton(Button["AutoVcControlView"]):
    def __init__(self):
        super().__init__(
            style=ButtonStyle.grey,
            label="Lock the channel",
            custom_id="phantomconstruct-autovc-control-lock",
            emoji="🔒"
        )

    async def callback(self, interaction: Interaction):
        if not self.view.is_owner(interaction):
            return await interaction.response.edit_message()
        await AutoVC.lock(interaction, self.view.bot)
        await self.view.update_msg(interaction.message)


class UnlockChannelButton(Button["AutoVcControlView"]):
    def __init__(self):
        super().__init__(
            style=ButtonStyle.grey,
            label="Unlock the channel",
            custom_id="phantomconstruct-autovc-control-unlock",
            emoji="🔓"
        )

    async def callback(self, interaction: Interaction):
        if not self.view.is_owner(interaction):
            return await interaction.response.edit_message()
        await AutoVC.lock(interaction, self.view.bot)
        await self.view.update_msg(interaction.message)


class OpenRenameModalButton(Button["AutoVcControlView"]):
    def __init__(self):
        super().__init__(
            style=ButtonStyle.grey,
            label="Rename the channel",
            custom_id="phantomconstruct-autovc-open-rename",
            emoji="✏️"
        )

    async def callback(self, interaction: Interaction):
        if not self.view.is_owner(interaction):
            return await interaction.response.edit_message()
        response: InteractionResponse = interaction.response
        return await response.send_modal(AutoVcRenameModalView())