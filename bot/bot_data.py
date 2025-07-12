import json
import dotenv
from attr import dataclass
from data_classes.birthday_data import BirthdayData
from entities import constants
import utils.ext_jsonencoder
import utils.dict_mapper
import data_classes.chat_fillters
from utils.dictify import Dictify

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
    chat_filters: "data_classes.ChatFilters" = data_classes.chat_fillters.ChatFilters()
    voice_log_channel: int = None
    user_whitelist: list[int] = []
    roles_whitelist: list[int] = []
    autovc_config: "data_classes.AutoVcConfig" = data_classes.AutoVcConfig()
    autovc_list: "dict[str, data_classes.DynamicVoicechatData]" = {}
    reminders: "dict[str, data_classes.ReminderData]" = {}
    birthdays: "list[BirthdayData]" = []
    birthday_channel_id: int = None

class _BotStateContextManager:
    def __init__(self, state, write = False):
        self._state = state
        self._write = write

    def __enter__(self):
        return self._state

    def __exit__(self, *args, **kwargs):
        if not self._write: return
        with open(env[constants.BOT_DATA], "w") as state_fd:
            json.dump(self.prepare_for_save(), state_fd, indent=2, cls=utils.ext_jsonencoder.ExtJsonEncoder)

    def prepare_for_save(self) -> dict[str, any]:
        return {k: Dictify.dictify(v) for k,v in
                [(k, v) for k,v in
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