from typing import List
import discord as d


class PollView(d.ui.View):
    def __init__(
            self,
            poll
    ):
        super().__init__(timeout=None)
        try:
            self.handler = poll.handler
            select_options = [d.SelectOption(label=a) for a in poll.answers]
            self.add_item(PollSelect(select_options, poll.choices))
        except:
            if self.handler:
                self.handler.delete_poll()


class PollSelect(d.ui.Select, d.ui.Item[PollView]):
    def __init__(
            self,
            options: List[d.SelectOption],
            choices: list[int, int]
    ):
        super().__init__(
            select_type=d.ComponentType.string_select,
            placeholder=f"Pick between {choices[0]} and {choices[1]}.",
            min_values=choices[0] or 1,
            max_values=choices[1] or 1,
            options=options
        )

    async def callback(self, interaction: d.Interaction):
        user_id = interaction.user.id
        votes = self.values
        self.view.handler.set_votes(user_id, votes)
        await interaction.response.send_message("Vote cast", ephemeral=True)

