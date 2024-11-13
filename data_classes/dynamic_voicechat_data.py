from attr import dataclass

from entities.autovc import AutoVC


@dataclass
class DynamicVoicechatData:
    channel_id: int = None
    owner_id: int = None
    password: str = None

    @classmethod
    def from_dynamic_voice_chat(cls, auto_vc: AutoVC) -> 'DynamicVoicechatData':
        return cls(
            channel_id=auto_vc.channel.id,
            owner_id=auto_vc.owner.id,
            password=auto_vc.password,
        )
