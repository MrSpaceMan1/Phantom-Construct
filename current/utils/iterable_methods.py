from typing import Callable, TypeVar, Collection, Generic

T = TypeVar("T")
U = TypeVar("U")

# class Stream(Generic[T]):
#     def __init(self, iterable: Collection[T]):
#         self.iter = iterable
#         self.comp = []


def find(iterable: Collection[T], fn: Callable[[T], bool]) -> int:
    for item, index in zip(iterable, range(len(iterable))):
        if fn(item):
            return index
    return -1

def map(iterable: Collection[T], fn: Callable[[T], U]) -> Collection[U]:
    return [fn(v) for v in iterable]