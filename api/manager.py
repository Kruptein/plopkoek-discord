import importlib
import os

from api.gateway import RtmHandler


def start_bots(threaded=False):
    g = RtmHandler()
    for fl in os.listdir("bots"):
        if fl.startswith("__") or not fl.endswith(".py"):
            continue

        mod = importlib.import_module("bots.{}".format(fl[:-3]))
        g.start_bot(getattr(mod, "{}Bot".format(fl[:-3].split("bot")[0].capitalize()))())
    g.run(threaded)
    return g

if __name__ == '__main__':
    start_bots(threaded=False)
