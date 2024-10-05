from autovc import AutoVC


class DynamicVoicechatData:
    def __init__(self, auto_vc: AutoVC):
        self.channel_id: int = ...
        self.password: str = ""
        self.max: int = -1
        ...