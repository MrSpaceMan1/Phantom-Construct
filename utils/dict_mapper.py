"""
Basic dict mapper. It uses type annotations to create dataclasses
"""

import typing

from constants import BUILTINS

T= typing.TypeVar("T")

class DictMapper:
    @staticmethod
    def map(dict_: dict[str, typing.Any], type_: typing.Type[T]) -> T:
        if not len(type_.__annotations__):
            raise Exception("Type has no known type annotations")
        mapped_obj: T = type_()
        for k, v in dict_.items():
            expected_type = type_.__annotations__[k]
            if expected_type in BUILTINS:
                mapped_obj.__dict__[k] = v
                continue

            if typing.get_origin(expected_type) is list:
                if typing.get_args(expected_type)[0] in BUILTINS:
                    mapped_obj.__dict__[k] = v
                    continue
                else:
                    print("kurwa, mamy problem")
                    continue

            if typing.get_origin(expected_type) is dict:
                type_args = typing.get_args(expected_type)
                if all([True if i not in BUILTINS else False for i in type_args]):
                    mapped_obj.__dict__[k] = v
                    continue
                mapped_dict = dict()
                for _k, _v in v.items():
                    mapped_dict[_k] = DictMapper.map(_v, type_args[1])
                mapped_obj.__dict__[k] = mapped_dict
                continue

            mapped_obj.__dict__[k] = DictMapper.map(v, expected_type)
        return mapped_obj