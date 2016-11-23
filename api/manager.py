import importlib
import os
import sys

from api.gateway import RtmHandler


def start_bots(threaded=False, bot=None):
    g = RtmHandler()
    if bot is None:
        for fl in os.listdir("bots"):
            if fl.startswith("__") or not fl.endswith(".py"):
                continue

            mod = importlib.import_module("bots.{}".format(fl[:-3]))
            g.start_bot(getattr(mod, "{}Bot".format(fl[:-3].split("bot")[0].capitalize()))())
    else:
        mod = importlib.import_module("bots.{}".format(bot))
        g.start_bot(getattr(mod, "{}Bot".format(bot.split("bot")[0].capitalize()))())
    g.run(threaded)
    return g

if __name__ == '__main__':
    if len(sys.argv) == 2:
        start_bots(threaded=False, bot=sys.argv[1])
    else:
        start_bots(threaded=False)
