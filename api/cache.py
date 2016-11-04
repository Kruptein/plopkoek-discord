from api.utils import get_value, set_value


def _get(var):
    return get_value('cache', var)


def _set(var, val):
    return set_value('cache', var, val)


def get_users():
    return _get("users")


def update_user(data):
    _set("users", dict(get_users(), **{data['id']: data}))
