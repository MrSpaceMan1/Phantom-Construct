import asyncio
import discord

number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "1️⃣1️⃣", "1️⃣2️", "1️2️", "1️3️"]


def finish_poll_task_creator(bot, view, time: float):
    async def disable_all_items():
        await asyncio.sleep(time)
        view.disable_all_items()

        aggregated = compile_answers(view.poll_id, bot)
        embed = create_results_embed(aggregated)

        await view.ctx.interaction.edit_original_message(embed=embed, view=view)

    asyncio\
        .get_event_loop()\
        .create_task(disable_all_items())


def compile_answers(_id: str, bot):
    poll_results: dict = bot.session["poll"][_id]
    aggregated = {}
    for value in poll_results.values():
        for answer in value:
            aggregated[answer] = (aggregated.get(answer) or 0) + 1

    return aggregated


def create_results_embed(aggregated_answers):
    aggregated = aggregated_answers
    _all = sum(aggregated.values())
    results = discord.Embed(title="Results: ", description=f"Votes: {_all}\n")
    n = 0
    for k, v in aggregated.items():
        # I just really hope nobody ever tries to add more than 13 answers
        results.description += f"{number_emojis[n]} {k} \n"
        n += 1
    results.description += "\n"
    n = 0

    for k, v in aggregated.items():
        results.description += f"{number_emojis[n]} " \
                               f"{'▓' * int(10 * v / _all)}" \
                               f"{'░' * int(10 * (_all - v) / _all)}" \
                               f" {int(v / _all * 100)}%\n"
        n += 1

    return results
