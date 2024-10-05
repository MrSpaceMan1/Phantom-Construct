from io import FileIO

from data_classes import ChatFilters, PollData, DynamicVoicechatData, ReminderData


class BotState:
    rules: list[str] = []
    bad_words: list[str] = []
    transcript_channel: int = None
    report_channel: int = None
    message_log_channel: int = None
    user_log_channel: int = None
    warning_log_channel: int = None
    poll_role: int = None
    autovc_channel: int = None
    chat_filters: "ChatFilters" = None
    voice_log_channel: int = None
    user_whitelist: list[int] = []
    roles_whitelist: list[int] = []
    polls: dict[str, "PollData"] = {}
    autovc_list: dict[str, "DynamicVoicechatData"] = {}
    reminders: dict[str, "ReminderData"] = {}
    def __init__(self):
        self.rules: list[str] = []
        self.bad_words: list[str] = []
        self.transcript_channel: int = None
        self.report_channel: int = None
        self.message_log_channel: int = None
        self.user_log_channel: int = None
        self.warning_log_channel: int = None
        self.poll_role: int = None
        self.autovc_channel: int = None
        self.chat_filters: "ChatFilters" = None
        self.voice_log_channel: int = None
        self.user_whitelist: list[int] = []
        self.roles_whitelist: list[int] = []
        self.polls: dict[str, "PollData"] = {}
        self.autovc_list: dict[str, "DynamicVoicechatData"] = {}
        self.reminders: dict[str, "ReminderData"] = {}

class _BotStateContextManager:
    def __init__(self, state: BotState, write: bool = False):
        self._state: BotState = ...
        self._write: bool = ...
        ...
    def __enter__(self) -> BotState:...
    def __exit__(self, *args, **kwargs) -> None:...
    def prepare_for_save(self) -> dict[str, any]:...

class BotStateManager:
    def __init__(self):
        self.__state: BotState = ...
    def init(self, state_fd: FileIO) -> None:...
    def access(self) -> _BotStateContextManager:...
    def access_write(self) -> _BotStateContextManager:...
