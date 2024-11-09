import datetime

from attr import dataclass


@dataclass
class BirthdayData:
    member_id: int = None
    date: tuple[int, int] = None
    next_trigger_year: int = None

    def get_date(self) -> datetime.date:
        month, day = self.date
        return datetime.date(self.next_trigger_year, month, day)