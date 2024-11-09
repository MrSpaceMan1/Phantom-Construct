from attr import dataclass
import entities.reminder


@dataclass
class ReminderData:
    content: str = None
    delay: tuple[int, int, int, int] = None
    next: float = None
    times: int = None
    channel_id: int = None

def from_reminder(rem: entities.reminder.Reminder):
    r = ReminderData()
    r.delay = rem.delay
    r.times = rem.times
    r.content = rem.content
    r.next = rem.next_timestamp
    r.channel_id = rem.channel.id
    return r