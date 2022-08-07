from typing import Optional, TextIO


class Storage:
    def __init__(self):
        self._data = {}

    @property
    def keys(self):
        return self._data.keys()

    def flush(self):
        self._data = {}

    def __setitem__(self, key, value) -> None:
        self._data[key] = value

    def __getitem__(self, key) -> Optional[str or int or list[int] or list[str]]:
        return self._data.get(key)

    def __repr__(self):
        return self._data.__repr__()


class JoinStorage(Storage):
    def __init__(self):
        super().__init__()

    def __getitem__(self, key) -> str or int or list[int] or list[str]:
        return self._data.get(key) or 0


class VolatileStorage:
    def __init__(self, bot):
        self.__data = {
            "join": JoinStorage(),
            "poll": Storage()
        }
        self.bot = bot

    def __call__(self) -> dict:
        return self.__data

    def __setitem__(self, key, value) -> None:
        self.__data[key] = value

    def __getitem__(self, key) -> Optional[str or int or list[int] or list[str]]:
        return self.__data.get(key)
