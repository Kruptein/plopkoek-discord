"""
A dummy bot that echoes.
Good test subject.
"""

import logging

from api.decorators import command
from api.gateway import Bot
from api.web import Channel


class EchoBot(Bot):
    """Dummy bot that is a simple rtm handler."""

    def __init__(self, stream_log_level=logging.DEBUG, file_log_level=logging.INFO):
        super().__init__("echo", stream_log_level=stream_log_level, file_log_level=file_log_level)

    @command('*', fmt='content>')
    def echo(self, event, args):
        Channel.create_message(channel_id=event.channel_id,
                               content='{} <:plop:236155120067411968>'.format(args.content))
