from attr import dataclass


@dataclass
class DynamicVoicechatData:
    channel_id: int = None
    password: str = None
    max: int = None