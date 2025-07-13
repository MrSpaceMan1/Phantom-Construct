import logging

from discord.abc import GuildChannel
from discord.ui import View, Select, Button
from discord import ComponentType, ChannelType, Interaction, ButtonStyle, Role, Thread

from logging import getLogger

from bot.my_bot import MyBot


class TriggerChannelSelect(Select):
    def __init__(self):
        super().__init__(select_type=ComponentType.channel_select, channel_types=[ChannelType.voice])

    async def callback(self, interaction: Interaction):
        await interaction.edit()

    @property
    def values(
        self,
    ) -> list[GuildChannel | Thread]:
        return super().values


class BaseRoleSelect(Select):
    def __init__(self):
        super().__init__(select_type=ComponentType.role_select)

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
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)
        self.trigger_channel = TriggerChannelSelect()
        self.base_role = BaseRoleSelect()
        self.submit_button = SubmitButton()
        super().__init__(self.trigger_channel, self.base_role, self.submit_button, timeout=1 * 60, disable_on_timeout=True)

    async def submit(self, interaction: Interaction):
        bot = MyBot.get_instance()
        with bot.data.access_write() as state:
            if selected := self.trigger_channel.values:
                trigger_channel = selected[0]
                state.autovc_config.trigger_channel_id = trigger_channel.id

            if selected := self.base_role.values:
                role = selected[0]
                state.autovc_config.base_role_id = role.id

        await interaction.edit(content="Config saved", view=None)
