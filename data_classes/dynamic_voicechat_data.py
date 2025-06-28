from attr import dataclass

from entities.autovc import AutoVC


@dataclass
class DynamicVoicechatRequests:
    user_id: int = None
    timeout: float = None # timestamp

    @classmethod
    def from_tuple(cls, user_id: int, timeout: float):
        return cls(user_id=user_id, timeout=timeout)

@dataclass
class DynamicVoicechatData:
    channel_id: int = None
    owner_id: int = None
    locked: bool = None
    requests: list[DynamicVoicechatRequests] = []

    @classmethod
    def from_dynamic_voice_chat(cls, auto_vc: AutoVC) -> 'DynamicVoicechatData':
        return cls(
            channel_id=auto_vc.channel.id,
            owner_id=auto_vc.owner.id,
            locked=auto_vc.locked,
            requests=auto_vc.requests
        )
