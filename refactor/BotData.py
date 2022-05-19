class BotData:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(BotData, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.data = dict()

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]
