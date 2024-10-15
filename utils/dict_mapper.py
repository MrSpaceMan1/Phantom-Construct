"""
Basic dict mapper. It uses type annotations to create dataclasses
"""

import typing

from entities.constants import BUILTINS

T= typing.TypeVar("T")

class DictMapper:
    @staticmethod
    def _map_class(dict_: dict[str, typing.Any], type_: typing.Type[T]) -> T:
        mapped_obj: T = type_()
        for k, v in dict_.items():
            expected_type = type_.__annotations__.get(k)
            if expected_type in BUILTINS:
                mapped_obj.__dict__[k] = v
                continue

            mapped_obj.__dict__[k] = DictMapper._determine_type(expected_type)(v, expected_type)
        return mapped_obj

    @staticmethod
    def _map_list(list_: list[typing.Any], type_: typing.Type[T]) -> list[T]:
        expected_type = typing.get_args(type_)[0]
        if expected_type in BUILTINS:
            return list_
        mapping_method = DictMapper._determine_type(expected_type)
        return [mapping_method(i, expected_type) for i in list_]

    @staticmethod
    def _map_dict(dict_: dict[str, typing.Any], type_: typing.Type[T]):
        expected_type = typing.get_args(type_)[1]
        if expected_type in BUILTINS:
            return dict_
        mapping_method = DictMapper._determine_type(expected_type)
        return {k:mapping_method(v, expected_type) for k, v in dict_.items()}


    @staticmethod
    def map(dict_: dict[str, typing.Any], type_: typing.Type[T]) -> T:
        method = DictMapper._determine_type(type_)
        return method(dict_, type_)

    @staticmethod
    def _determine_type(type_: typing.Type[T]) -> typing.Callable[[typing.Any, typing.Type[T]], T]:
        try:
            if type_.__annotations__:
                return DictMapper._map_class
        except:
            pass
        if typing.get_origin(type_) is list:
            return DictMapper._map_list
        if typing.get_origin(type_) is dict:
            return DictMapper._map_dict
        raise TypeError("Type has no known type annotations")