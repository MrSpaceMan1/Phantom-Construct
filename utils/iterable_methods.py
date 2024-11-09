from typing import TypeVar, Collection, Callable

_T = TypeVar("_T")
_U = TypeVar("_U")

def find(iterable: Collection[_T], fn: Callable[[_T], bool]) -> int:
    for item, index in zip(iterable, range(len(iterable))):
        if fn(item):
            return index
    return -1


def map_(iterable: Collection[_T], fn: Callable[[_T], _U]) -> list[_U]:
    return [fn(v) for v in iterable]


async def async_map(iterable: Collection[_T], fn: Callable[[_T], _U]) -> list[_U]:
    return [await fn(v) for v in iterable]
