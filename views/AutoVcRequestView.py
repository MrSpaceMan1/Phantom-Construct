from typing import TYPE_CHECKING, Optional

from discord.ui import View, Button
from discord import ButtonStyle, Interaction, Member

from entities import AutoVC
from utils.iterable_methods import find

if TYPE_CHECKING:
    from bot.my_bot import MyBot


class AutoVcRequestView(View):
    def __init__(self, bot: "MyBot"):
        self.bot = bot
        super().__init__(
            AcceptRequest(),
            DenyRequest(),
            timeout=None
        )

    def get_user_by_interaction(self, interaction: Interaction) -> Optional[Member]:
        with self.bot.data.access() as state:
            autovc_data = state.autovc_list.get(str(interaction.channel.id))
            if not autovc_data:
                return None

            index = find(autovc_data.requests, lambda r: r.message_id == interaction.message.id)
            if index >= 0:
                return interaction.guild.get_member(autovc_data.requests[index].user_id)
        return None

    def remove_request_by_interaction(self, interaction: Interaction):
        with self.bot.data.access() as state:
            autovc_data = state.autovc_list.get(str(interaction.channel.id))
            if not autovc_data:
                return

            index = find(autovc_data.requests, lambda r: r.message_id == interaction.message.id)
            if index >= 0:
                autovc_data.requests.pop(index)

    async def on_timeout(self) -> None:
        await self.message.delete()


class AcceptRequest(Button["AutoVcRequestView"]):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            style=ButtonStyle.success,
            label="Accept request",
            emoji="✔",
            custom_id=f"phantomconstruct-accept-join-request",
        )

    async def callback(self, interaction: Interaction):
        await interaction.respond("Accepted", ephemeral=True)
        if user := self.view.get_user_by_interaction(interaction):
            await AutoVC.join(user, interaction.channel, self.view.bot)
        await self.view.on_timeout()


class DenyRequest(Button["AutoVcRequestView"]):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            style=ButtonStyle.danger,
            label="Deny request",
            emoji= "✖",
            custom_id=f"phantomconstruct-deny-join-request",
        )


    async def callback(self, interaction: Interaction):
        await interaction.respond("Denied", ephemeral=True)
        if user := self.view.get_user_by_interaction(interaction):
            await user.send("Your request to join has been denied.")
        await self.view.on_timeout()