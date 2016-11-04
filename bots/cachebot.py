"""
A dummy bot that echoes.
Good test subject.
"""

import logging
import os

from api.gateway import Bot
from api.utils import set_value


class CacheBot(Bot):
    """Dummy bot that is a simple rtm handler."""

    def __init__(self, stream_log_level=logging.DEBUG, file_log_level=logging.INFO):
        super().__init__("cache", stream_log_level=stream_log_level, file_log_level=file_log_level)
        set_value("cachebot", "pid", os.getpid())


if __name__ == "__main__":
    CacheBot().run(False)
