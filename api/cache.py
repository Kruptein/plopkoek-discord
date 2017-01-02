from api.utils import get_value, set_value


def _get(var):
    return get_value('cache', var)


def _set(var, val):
    return set_value('cache', var, val)


def get_users():
    return _get("users")


def get_channels():
    return _get("channels")


def get_guilds():
    return _get("guilds")


def update_user(data):
    try:
        _set("users", dict(get_users(), **{data['id']: data}))
    except KeyError:
        print("Failed to update user data {}".format(data))


def update_channel(data):
    _set("channels", dict(get_channels(), **{data['id']: data}))


def remove_channel(channel_id):
    channels = get_channels()
    del channels[channel_id]
    _set("channels", channels)


def update_guild(data):
    _set("guilds", dict(get_guilds(), **{data['id']: data}))


def remove_guild(data):
    guilds = get_guilds()
    guild = guilds[data['id']]
    del guilds[data['id']]
    for channel in guild['channels']:
        remove_channel(channel['id'])
    _set("guilds", guilds)
