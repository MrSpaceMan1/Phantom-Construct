import json
import dotenv
from attr import dataclass
import constants
import utils.ext_jsonencoder
import utils.dict_mapper
from data_classes import ChatFilters, PollData, DynamicVoicechatData, ReminderData

env = dotenv.dotenv_values()

@dataclass
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
    chat_filters: ChatFilters = None
    voice_log_channel: int = None
    user_whitelist: list[int] = []
    roles_whitelist: list[int] = []
    polls: dict[str, PollData] = {}
    autovc_list: dict[str, DynamicVoicechatData] = {}
    reminders: dict[str, ReminderData] = {}

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
    __state: BotState

    def init(self, state_fd):
        state: dict = json.load(state_fd)
        self.__state = utils.dict_mapper.DictMapper.map(state, BotState)

    def access(self):
        return _BotStateContextManager(self.__state)

    def access_write(self):
        return _BotStateContextManager(self.__state, write=True)