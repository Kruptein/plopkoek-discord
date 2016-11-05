"""
A collection of decorators.
"""

from functools import wraps

from api import local
from api import utils
from api.exceptions import NotCachedException


def cache(update_func):
    """
    If CacheBot is running, try to fetch a cached version of the function call.
    Else just run the actual function.
    """
    def inner_cache(orig_func):
        @wraps(orig_func)
        def decorator(*args, **kwargs):
            if not utils.USE_CACHE:
                return orig_func(*args, **kwargs)

            try:
                cls, f = orig_func.__qualname__.split(".")
                local_func = getattr(getattr(local, cls), f)
            except AttributeError:
                # there is no local version of this endpoint, so return live function
                return orig_func(*args, **kwargs)
            else:
                try:
                    return local_func(*args, **kwargs)
                except NotCachedException:
                    # Use the live version and cache the value
                    data = orig_func(*args, **kwargs)
                    update_func(data)
                    return data
        return decorator
    return inner_cache


def command(*names):
    """
    Registers the provided names as aliases for the decorated function.
     Usage: @command('commandname') or @command('name1', 'name2', ..., 'nameN')
    """
    def decorator(func):
        func.command = names
        return func
    return decorator
