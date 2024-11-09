from typing import Any, Iterable, SupportsIndex

from entities.constants import BUILTINS


class Dictify:
    @staticmethod
    def dictify(o: Any):
        if type(o) in BUILTINS:
            return o
        if type(o) is list:
            return Dictify._dictify_iterable(o)
        if type(o) is dict:
            return Dictify._dictify_dict(o)
        if type(o) is tuple:
            return Dictify._dictify_tuple(o)
        return Dictify._dictify_obj(o)

    @staticmethod
    def _dictify_tuple(o: tuple):
        return tuple([Dictify.dictify(i) for i in o])

    @staticmethod
    def _dictify_dict(o: dict):
        return {k: Dictify.dictify(v) for k,v in o.items()}

    @staticmethod
    def _dictify_iterable(o: Iterable):
        return [Dictify.dictify(v) for v in o]

    @staticmethod
    def _dictify_obj(o: Any):
        return {k: Dictify.dictify(v) for k, v in vars(o).items()}