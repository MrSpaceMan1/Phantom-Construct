from typing import Optional, Union

class Storage:
    def __init__(self):
        self._data: dict[str, Optional[Union[str, int, list[str], list[int]]]] = ...
        ...
    @property
    def keys(self):...
    def flush(self) -> None:...
    def __setitem__(self, key, value) -> None:...
    def __getitem__(self, key) -> Optional[Union[str, int, list[str], list[int]]]:...
    def __repr__(self) -> str:...
class JoinStorage(Storage):...
class VolatileStorage:
    def __init__(self):
        self.__data: dict[str, Storage] = ...
    def __call__(self) -> dict[str, Storage]:...
    def __setitem__(self, key, value) -> None:...
    def __getitem__(self, key) -> Optional[Union[str, int, list[str], list[int]]]:...