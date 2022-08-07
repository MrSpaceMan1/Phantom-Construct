import discord.ui
from typing import List
from current.utils.MyBot import MyBot
from current.utils.pollUtils import compile_answers, create_results_embed

class Poll(discord.ui.View):
    def __init__(
            self,
            bot: MyBot,
            ctx: discord.ApplicationContext,
            question: str,
            id: str,
            options: List[discord.components.SelectOption],
            max_choices=1,
            placeholder=None
    ):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.question = question
        self.bot = bot
        self.poll_id = id
        self.add_item(
            PollSelect(
                bot=bot,
                ctx=ctx,
                id=id,
                options=options,
                max_choices=max_choices,
                placeholder=placeholder)
        )


class PollSelect(discord.ui.Select):
    def __init__(
            self,
            bot: MyBot,
            ctx: discord.ApplicationContext,
            id: str,
            options: List[discord.components.SelectOption],
            max_choices=1,
            placeholder=None
    ):
        super().__init__(custom_id=id, options=options, placeholder=placeholder, max_values=max_choices)
        self.ctx = ctx
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        user_id: int = interaction.user.id
        self.bot.session["poll"][self.custom_id][user_id] = self.values

        embed = create_results_embed(compile_answers(self.custom_id, self.bot))

        await self.ctx.interaction.edit_original_message(embed=embed)
        await interaction.response.send_message("Vote cast", ephemeral=True)
