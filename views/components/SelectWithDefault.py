from typing import TypedDict, Optional

from discord import ComponentType, SelectOption, ChannelType, InvalidArgument, Role, User
from discord.abc import Messageable
from discord.ui import Select

def class_to_type(obj):
    if isinstance(obj, Messageable):
        return "channel"
    if isinstance(obj, Role):
        return "role"
    if isinstance(obj, User):
        return "user"


class DefaultValuesPayload(TypedDict):
    type: str
    id: int


class SelectWithDefault(Select):
    def __init__(self,  select_type: ComponentType = ComponentType.string_select,
        *,
        custom_id: str | None = None,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        options: list[SelectOption] = None,
        channel_types: list[ChannelType] = None,
        disabled: bool = False,
        row: int | None = None,
        default_values: list[Role | User | Messageable] = None):

        super().__init__(
        select_type=select_type,
        custom_id=custom_id,
        placeholder=placeholder,
        min_values=min_values,
        max_values=max_values,
        options=options,
        channel_types=channel_types,
        disabled=disabled,
        row=row)

        self._default_values: list[Role | User | Messageable] = None

        if not default_values:
            return

        if select_type not in [
            ComponentType.channel_select,
            ComponentType.mentionable_select,
            ComponentType.role_select,
            ComponentType.user_select
        ]:
            raise InvalidArgument("default_values can only be used with select of type: channel_select, "
                                  "mentionable_select, role_select, user_select")

        if not (min_values <= len(default_values) <= max_values):
            raise InvalidArgument("Default values length must be between min_values and max_values")

        if (select_type is ComponentType.channel_select and
            not all([True if isinstance(value, Messageable) else False for value in default_values])):
            raise InvalidArgument("Default values must all be channels for select of type channel_select")

        if (select_type is ComponentType.role_select and
            not all([True if isinstance(value, Role) else False for value in default_values])):
            raise InvalidArgument("Default values must all be roles for select of type role_select")

        if (select_type is ComponentType.user_select and
            not all([True if isinstance(value, User) else False for value in default_values])):
            raise InvalidArgument("Default values must all be users for select of type user_select")

        if (select_type is ComponentType.mentionable_select and
            not all([True if any([isinstance(value, Role), isinstance(value, User), isinstance(value, Messageable)])
                     else False
                     for value in default_values])):
            raise InvalidArgument("Default values must all be mentionable for select of type mentionable_select")

        self._default_values = default_values

    @property
    def default_values(self) -> Optional[list[Role | User | Messageable]]:
        return self._default_values

    def default_values_to_dict(self, default_values: list[Role | User | Messageable]) -> list[DefaultValuesPayload]:
        return [
            DefaultValuesPayload(
                type=class_to_type(value),
                id=value.id
            ) for value in default_values
        ]

    def to_component_dict(self):
        payload = super().to_component_dict()
        if getattr(self, "_default_values", None):
            payload["default_values"] = self.default_values_to_dict(self._default_values)
        return payload