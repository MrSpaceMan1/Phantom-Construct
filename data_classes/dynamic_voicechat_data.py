class DynamicVoicechatData:
    def __init__(self, auto_vc):
        self.channel_id: int = auto_vc.channel.id
        self.password: str = ""
        self.max: int = -1