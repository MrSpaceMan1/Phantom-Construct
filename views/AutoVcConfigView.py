from typing import Optional, TypeVar, Callable, Any

from discord.abc import GuildChannel
from discord.types.channel import Channel
from discord.ui import View, Button
from discord import ComponentType, ChannelType, Interaction, ButtonStyle, Role, Thread

from bot.my_bot import MyBot
from views.components.SelectWithDefault import SelectWithDefault


class TriggerChannelSelect(SelectWithDefault):
    def __init__(self, trigger_channel: Optional[Channel] = None):
        default_values = None
        if trigger_channel:
            default_values = [trigger_channel]

        super().__init__(
            select_type=ComponentType.channel_select,
            channel_types=[ChannelType.voice],
            min_values=0,
            default_values=default_values
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.edit()

    @property
    def values(
        self,
    ) -> list[GuildChannel | Thread]:
        return super().values


class BaseRoleSelect(SelectWithDefault):
    def __init__(self, base_role: Optional[Role] = None):
        default_values = None
        if base_role:
            default_values = [base_role]

        super().__init__(
            select_type=ComponentType.role_select,
            min_values=0,
            default_values=default_values
        )



    async def callback(self, interaction: Interaction):
        await interaction.edit()

    @property
    def values(
            self,
    ) -> list[Role]:
        return super().values

class SubmitButton(Button["AutoVcConfigView"]):
    def __init__(self):
        super().__init__(style=ButtonStyle.blurple, label="Submit")

    async def callback(self, interaction: Interaction):
        await interaction.edit()
        await self.view.submit(interaction)

class AutoVcConfigView(View):
    def __init__(
        self,
        bot: "MyBot",
        base_role: Optional[Role] = None,
        trigger_channel: Optional[Channel] = None
    ):
        self.bot: "MyBot" = bot
        self.trigger_channel = TriggerChannelSelect(trigger_channel=trigger_channel)
        self.base_role = BaseRoleSelect(base_role=base_role)
        self.submit_button = SubmitButton()
        super().__init__(
            self.trigger_channel,
            self.base_role,
            self.submit_button,
            timeout=1 * 60,
            disable_on_timeout=True
        )

    async def submit(self, interaction: Interaction):
        with self.bot.data.access_write() as state:
            T = TypeVar("T")
            def next_or_none(iterable: list[T], select_key: Callable[[T], Any]) -> Optional[Any]:
                if iterable:
                   return select_key(iterable[0])
                return None

            if self.trigger_channel.values is not None:
                selected = self.trigger_channel.values
                channel_id = next_or_none(selected, lambda x: x.id)
                state.autovc_config.trigger_channel_id = channel_id
            else:
                state.autovc_config.trigger_channel_id = next_or_none(self.trigger_channel.default_values, lambda x: x.id)

            if self.base_role.values is not None:
                selected = self.base_role.values
                role_id = next_or_none(selected, lambda x: x.id)
                state.autovc_config.base_role_id = role_id
            else:
                state.autovc_config.base_role_id = next_or_none(self.base_role.default_values, lambda x: x.id)

        await interaction.edit(content="Config saved", view=None)
