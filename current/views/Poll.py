from typing import List, Optional
import discord as d

from current.utils.poll_utils import PollHandler


class Poll(d.ui.View):
    def __init__(
            self,
            pollHandler: PollHandler,
            answers: List[d.SelectOption],
            poll_id: str,
            choices: tuple[int, int]
    ):
        super().__init__(timeout=60)
        self.id = poll_id
        self.handler = pollHandler
        self.add_item(PollSelect(answers, poll_id, choices))

    async def on_timeout(self) -> None:
        self.disable_all_items()
        results = self.handler.get_results()
        self.handler.finish_poll()

        results_str = "\n".join(map(lambda x: ": ".join(x), results.items())) or None
        if results_str:
            return await self.message.edit(content=results_str, view=None)
        await self.message.delete(reason="Poll has ended")


class PollSelect(d.ui.Select, d.ui.Item[Poll]):
    def __init__(
            self,
            options: List[d.SelectOption],
            poll_id: str,
            choices: tuple[Optional[int], int]
    ):
        super().__init__(
            select_type=d.ComponentType.string_select,
            placeholder=f"Pick between {choices[0]} and {choices[1]}.",
            custom_id=poll_id,
            min_values=choices[0] or 1,
            max_values=choices[1] or 1,
            options=options
        )

    async def callback(self, interaction: d.Interaction):
        user_id = interaction.user.id
        votes = self.values
        self.view.handler.set_votes(user_id, votes)
        await interaction.response.send_message("Vote cast", ephemeral=True)
