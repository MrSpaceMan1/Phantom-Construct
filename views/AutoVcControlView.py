from typing import TYPE_CHECKING

from discord.ui import View, Button
from discord import Message, ButtonStyle, Interaction, InteractionResponse
from entities.autovc import AutoVC
from views.AutoVcRenameModal import AutoVcRenameModalView

if TYPE_CHECKING:
    from bot.my_bot import MyBot


class AutoVcControlView(View):
    def __init__(self, bot: "MyBot"):
        super().__init__(LockChannelButton(), OpenRenameModalButton(), timeout=None)
        self.bot = bot

    async def update_msg(self, msg: Message):
        with self.bot.data.access() as state:
            self.clear_items()
            channel_data = state.autovc_list.get(str(msg.channel.id))
            if not channel_data:
                return

            if channel_data.locked:
                self.add_item(UnlockChannelButton())
            else:
                self.add_item(LockChannelButton())

            self.add_item(OpenRenameModalButton())

        await msg.edit(view=self)


class LockChannelButton(Button["AutoVcControlView"]):
    def __init__(self):
        super().__init__(
            style=ButtonStyle.grey,
            label="Lock the channel",
            custom_id="phantomconstruct-autovc-control-lock",
            emoji="🔒"
        )

    async def callback(self, interaction: Interaction):
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
        response: InteractionResponse = interaction.response
        await response.send_modal(AutoVcRenameModalView())