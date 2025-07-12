from dataclasses import dataclass


@dataclass
class AutoVcConfig:
    trigger_channel_id: int = None
    base_role_id: int = None