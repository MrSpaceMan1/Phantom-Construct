from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.autovc import AutoVC


@dataclass
class DynamicVoicechatRequests:
    user_id: int = None
    timeout: float = None # timestamp
    message_id: int = None

    @classmethod
    def from_tuple(cls, user_id: int, timeout: float, message_id: int):
        return cls(user_id=user_id, timeout=timeout, message_id=message_id)

@dataclass
class DynamicVoicechatData:
    channel_id: int = None
    owner_id: int = None
    locked: bool = None
    requests: list[DynamicVoicechatRequests] = field(default_factory=list)

    @classmethod
    def from_dynamic_voice_chat(cls, auto_vc: "AutoVC") -> 'DynamicVoicechatData':
        return cls(
            channel_id=auto_vc.channel.id,
            owner_id=auto_vc.owner.id,
            locked=auto_vc.locked,
            requests=auto_vc.requests
        )
