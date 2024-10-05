import reminder

class ReminderData:
    def __init__(self, reminder_: reminder.Reminder):
        self.content: str = reminder_.content
        self.delay: list[int, int, int ,int] = reminder_.delay
        self.next: float = reminder_.next_timestamp
        self.channel_id: int = reminder_.channel.id