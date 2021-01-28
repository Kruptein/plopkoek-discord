"""
A collection of various utilities.
"""
import json
import os
import threading

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_VERSION = 6

WRITE_LOCK = threading.Lock()


def has_config(name) -> bool:
    return os.path.exists(os.path.join(ROOTDIR, "config", name))


def get_data(name):
    """
    Retrieves the content of the config file for the given name.
    These config files are supposed to be located in the "config" directory.
    """
    cfgpath = os.path.join(ROOTDIR, "config", name)
    open(cfgpath, "a").close()  # create cfg file if it doesnt exist

    with open(cfgpath, "r") as f:
        data = json.load(f)

    return data


def set_data(name, data):
    cfgpath = os.path.join(ROOTDIR, "config", name)
    with WRITE_LOCK:
        with open(cfgpath, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)


def get_value(name, var):
    """
    Read the `var` value from the config for `name`.
    """
    return get_data(name)[var]


def set_value(name, var, value):
    """
    Set the `var` value from the config for `name` to `value`.
    """
    data = get_data(name)
    data[var] = value
    set_data(name, data)


def pop_value(name, var, value):
    data = get_value(name, var)
    pop = data.pop(value)
    set_value(name, var, data)
    return pop


def append_value(name, var, value):
    data = get_value(name, var)
    data.append(value)
    set_value(name, var, data)


def update_value(name, var, key, value):
    data = get_value(name, var)
    data[key] = value
    set_value(name, var, data)
