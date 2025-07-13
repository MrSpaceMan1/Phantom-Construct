from discord import InputTextStyle, Interaction
from discord.ui import Modal, InputText

from bot.my_bot import MyBot
from entities import AutoVC

class AutoVcRenameModalView(Modal):
    def __init__(self):
        self.rename_input_text = RenameInputText()
        self.bot = MyBot.get_instance()
        super().__init__(self.rename_input_text, title="Rename the channel", timeout=1 * 60)
        
    async def callback(self, interaction: Interaction):
        new_name = self.rename_input_text.value
        await AutoVC.rename(new_name, interaction=interaction, bot=self.bot)


class RenameInputText(InputText):
    def __init__(self):
        super().__init__(style=InputTextStyle.short, label="New name")