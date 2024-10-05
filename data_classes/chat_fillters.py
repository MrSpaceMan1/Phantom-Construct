class ChatFilters:
    def __init__(self):
        self.suppress_bad_words: bool = False
        self.suppress_bad_words_edit: bool = False
        self.no_all_caps: bool = False
        self.no_all_caps_edit: bool = False
        self.no_d_links: bool = False
        self.no_d_links_edit: bool = False
        self.prevent_mass_mentions: bool = False
        self.prevent_join_spam: bool = False
        self.no_discord_links: bool = False
        self.no_discord_links_edit: bool = False

    def get(self, name: str) -> bool:
            return self.__dict__[name]