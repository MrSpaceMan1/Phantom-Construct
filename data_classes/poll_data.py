class VotesData:
    member_id: int
    votes: list[str]

class PollData:
    id: str
    finish: float
    votes: dict[int, VotesData]
    answers: list[str]
    choices: list[int, int]
    msg_id: int
    msg_channel_id: int
    guild_id: int

