from attr import dataclass

@dataclass
class VotesData:
    member_id: int = None
    votes: list[str] = None

@dataclass
class PollData:
    id: str = None
    finish: float = None
    votes: dict[int, VotesData] = None
    answers: list[str] = None
    choices: list[int, int] = None
    msg_id: int = None
    msg_channel_id: int = None
    guild_id: int = None
