from attr import dataclass


@dataclass
class ReminderData:
    content: str = None
    delay: list[int, int, int, int] = None
    next: float = None
    channel_id: int = None