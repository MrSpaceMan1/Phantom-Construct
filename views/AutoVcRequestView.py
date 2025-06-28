import logging
from typing import TYPE_CHECKING
from discord.ui import View, Button
from discord import ButtonStyle, Interaction

if TYPE_CHECKING:
    from discord import Component


class AutoVcRequestView(View):
    def get_custom_id(self, component: "Component"):
        custom_id = f"{component.__class__.__name__}-{self.channel_id}-{self.request_user_id}"
        return custom_id


    def __init__(self, request_user_id: int, channel_id: int):
        self.request_user_id = request_user_id
        self.channel_id = channel_id
        super().__init__(
            AcceptRequest(request_user_id, channel_id),
            DenyRequest(request_user_id, channel_id),
            timeout=None
        )

        logging.log(logging.INFO, f"AutoVcRequestView is {self.is_persistent()}")

    async def on_timeout(self) -> None:
        await self.message.delete()


class AcceptRequest(Button):
    def __init__(self, request_user_id: int, channel_id: int, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            style=ButtonStyle.success,
            label="Accept request",
            emoji="✔",
            custom_id=f"{self.__class__.__name__}-{channel_id}-{request_user_id}",
        )

    async def callback(self, interaction: Interaction):
        await interaction.respond("Accepted", ephemeral=True)
        user = interaction.guild.get_member(self.view.request_user_id)
        if getattr(user.voice, "channel", None):
            await user.move_to(interaction.channel)
        else:
            await user.send("We tried to move you, but you weren't in a voice chat at the time. "
                            "Try again or ask admins to help you.")
        await self.view.on_timeout()


class DenyRequest(Button):
    def __init__(self, request_user_id: int, channel_id: int, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            style=ButtonStyle.danger,
            label="Deny request",
            emoji= "✖",
            custom_id=f"{self.__class__.__name__}-{channel_id}-{request_user_id}",
        )

    async def callback(self, interaction: Interaction):
        await interaction.respond("Denied", ephemeral=True)
        user = interaction.guild.get_member(self.view.request_user_id)
        await user.send("Your request to join has been denied.")
        await self.view.on_timeout()