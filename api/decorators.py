"""
A collection of decorators.
"""

from functools import wraps

from api import local
from api.utils import USE_CACHE


def cache(func):
    """
    If CacheBot is running, try to fetch a cached version of the function call.
    Else just run the actual function.
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        if not USE_CACHE:
            return func(*args, **kwargs)

        try:
            cls, f = func.__qualname__.split(".")
            local_func = getattr(getattr(local, cls), f)
        except AttributeError:
            # there is no local version of this endpoint, so return live function
            return func(*args, **kwargs)
        else:
            return local_func(*args, **kwargs)
    return decorator


def command(*names):
    """
    Registers the provided names as aliases for the decorated function.
     Usage: @command('commandname') or @command('name1', 'name2', ..., 'nameN')
    """
    def decorator(func):
        func.command = names
        return func
    return decorator
