import json
import typing
from pprint import pprint

import dotenv
import constants
import utils.ext_jsonencoder
from constants import BUILTINS
from data_classes import ChatFilters, PollData, DynamicVoicechatData, ReminderData

env = dotenv.dotenv_values()

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
    def __init__(self, state, write = False):
        self._state = state
        self._write = write

    def __enter__(self):
        return self._state

    def __exit__(self, *args, **kwargs):
        if not self._write: return
        with open(env[constants.BOT_DATA], "w") as state_fd:
            json.dump(self.prepare_for_save(), state_fd, indent=2, cls=utils.ext_jsonencoder.ExtJSONEncoder)

    def prepare_for_save(self) -> dict[str, any]:
        return {k: v for k, v in
                [(k, v) for k, v in
                 vars(self._state).items() if not k.startswith("_BotState__") or not k.startswith("_")]}


class BotStateManager:
    def __init__(self):
        self.__state = BotState()

    def init(self, state_fd):
        state: dict = json.load(state_fd)
        fields = vars(self.__state).keys()
        for k, v in state.items():
            if k not in fields:
                raise ValueError(f"Unknown key: {k} not in state")
            expected_type = self.__state.__annotations__[k]
            if expected_type not in BUILTINS:
                type_args = typing.get_args(expected_type)
                if

            self.__state.__dict__[k] = v

    def access(self):
        return _BotStateContextManager(self.__state)

    def access_write(self):
        return _BotStateContextManager(self.__state, write=True)