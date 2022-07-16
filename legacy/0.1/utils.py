command_permissions = dict()
ignored_channels = set()
ignored_users = set()
ignored_roles = set()


class BadWords:
    instance = None

    def __init__(self):
        self._words = []
        if BadWords.instance is None:
            BadWords.instance = self

    @property
    def words(self):
        return self._words

    @words.setter
    def words(self, val):
        self._words = val


class IsIgnored(Exception):
    pass


async def no_premissions(ctx):
    await ctx.respond("⛔ Insufficient permissions ⛔", ephemeral=True)


async def reply(ctx, msg):
    await ctx.respond(msg, ephemeral=True)
    return


def is_ignored(channel, user):
    if channel.id in ignored_channels:
        raise IsIgnored
    if user.id in ignored_users:
        raise IsIgnored
    for role in user.roles:
        if role in ignored_roles:
            raise IsIgnored
