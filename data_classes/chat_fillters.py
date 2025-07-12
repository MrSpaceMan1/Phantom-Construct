from dataclasses import dataclass


@dataclass
class ChatFilters:
    suppress_bad_words: bool = False
    suppress_bad_words_edit: bool = False
    no_all_caps: bool = False
    no_all_caps_edit: bool = False
    no_d_links: bool = False
    no_d_links_edit: bool = False
    prevent_mass_mentions: bool = False
    prevent_join_spam: bool = False
    no_discord_links: bool = False
    no_discord_links_edit: bool = False

    def get(self, name: str) -> bool:
            return self.__dict__[name]

    def update(self, name: str, value: bool) -> None:
        self.__dict__[name] = value

    def items(self) -> dict[str, bool]:
        return self.__dict__.items()