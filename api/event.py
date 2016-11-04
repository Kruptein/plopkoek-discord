import sys

from enum import IntEnum

from api import cache
from api.utils import get_logger


module = sys.modules[__name__]


def __to_classname(event_name: str):
    return "".join(part.capitalize() for part in event_name.split("_"))


def get_event(json_data) -> 'Event':
    if json_data['op'] == 0 and hasattr(module, __to_classname(json_data['t'])):
        return getattr(module, __to_classname(json_data['t']))(json_data)
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
            get_logger('main').exception("Could not extrapolate data from event. {}".format(data))

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


class Ready(Event):
    def __init__(self, data):
        super().__init__(data)
        cache.update_user(self.user)
        for channel in self.private_channels:
            cache.update_user(channel['recipient'])
