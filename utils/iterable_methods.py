def find(iterable, fn):
    for item, index in zip(iterable, range(len(iterable))):
        if fn(item):
            return index
    return -1


def map(iterable, fn):
    return [fn(v) for v in iterable]


async def async_map(iterable, fn):
    return [await fn(v) for v in iterable]
