import logging

from enum import IntEnum

from utils import get_logger


def get_event(json_data) -> 'Event':
    return Event(json_data)


class GatewayOP(IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    STATUS_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    VOICE_SERVER_PING = 5
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class Event:
    def __init__(self, data):
        self._s = data['s']
        self._t = data['t']
        self._op = data['op']
        self.raw_data = data

        try:
            if data['d'] is not None:
                for var in data['d']:
                    setattr(self, var, data['d'][var])
        except:
            get_logger('main').exception("Could not extrapolate data from event.")

        self.is_dispatch = self.of(GatewayOP.DISPATCH)

    @property
    def sequence(self):
        return self._s

    def of(self, op_code):
        return self._op == op_code

    def of_t(self, type_):
        return self._t == type_

    def __repr__(self):
        return "Event({})".format(self._t)
