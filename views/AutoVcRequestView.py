from typing import TYPE_CHECKING, Optional

from discord.ui import View, Button
from discord import ButtonStyle, Interaction, Member

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
            if getattr(user.voice, "channel", None):
                await user.move_to(interaction.channel)
            else:
                await user.send("We tried to move you, but you weren't in a voice chat at the time. "
                                "Try again or ask admins to help you.")

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