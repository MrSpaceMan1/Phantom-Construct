import json
import typing
import datetime

from entities import constants


class ExtJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) is datetime.date:
            return typing.cast(datetime.date, o).isoformat()
        return super().default(o)

class ExtJsonDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        try:
            return datetime.date.fromisoformat(s)
        except TypeError:
            pass

        return super().decode(s, **kwargs)