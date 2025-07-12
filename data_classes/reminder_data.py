from typing import TYPE_CHECKING

from dataclasses import dataclass

if TYPE_CHECKING:
    from entities import Reminder

@dataclass
class ReminderData:
    content: str = None
    delay: tuple[int, int, int, int] = None
    next: float = None
    times: int = None
    channel_id: int = None
    username: str = None

    @classmethod

    def from_reminder(cls, rem: "Reminder"):
        return cls(
            delay=rem.delay,
            times=rem.times,
            content=rem.content,
            next=rem.next_timestamp,
            channel_id=rem.channel.id,
            username=rem.username
        )