"""
A dummy bot that echoes.
Good test subject.
"""

import logging

from api.gateway import Bot
from api.web import Channel


class EchoBot(Bot):
    """Dummy bot that is a simple rtm handler."""

    def __init__(self, stream_log_level=logging.DEBUG, file_log_level=logging.INFO):
        super().__init__("echo", stream_log_level=stream_log_level, file_log_level=file_log_level)

    def execute_bot_event(self, event, commands):
        super().is_bot_command(event)
        Channel.create_message(channel_id=event.channel_id,
                               content='{} <:plop:236155120067411968>'.format(event.content[len('!echo '):]))


if __name__ == "__main__":
    EchoBot().run(False)
