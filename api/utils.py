"""
A collection of various utilities.
"""
import json
import logging
import os
import pickle
from enum import IntEnum

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_VERSION = 5
USE_CACHE = False


class ConfigFormat(IntEnum):
    JSON = 0
    PICKLE = 1


def activate_cache():
    global USE_CACHE
    USE_CACHE = True


def get_log_path(name):
    return os.path.join(ROOTDIR, "logs", "{}.log".format(name))


def get_logger(name, file_log_level=logging.INFO, stream_log_level=logging.INFO):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(threadName)s: %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add file logger
    path = get_log_path(name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fh = logging.FileHandler(path)
    fh.setLevel(file_log_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # add stream logger
    sh = logging.StreamHandler()
    sh.setLevel(stream_log_level)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


def has_config(name) -> bool:
    return os.path.exists(os.path.join(ROOTDIR, "config", name))


def get_data(name, data_format=ConfigFormat.JSON):
    """
    Retrieves the content of the config file for the given name.
    These config files are supposed to be located in the "config" directory.
    """
    cfgpath = os.path.join(ROOTDIR, "config", name)
    open(cfgpath, 'a').close()  # create cfg file if it doesnt exist
    try:
        if data_format == ConfigFormat.JSON:
            with open(cfgpath, 'r') as f:
                data = json.load(f)
        elif data_format == ConfigFormat.PICKLE:
            with open(cfgpath, 'rb') as f:
                data = pickle.load(f)
        else:
            raise Exception("Unknown dataformat")
    except (EOFError, ValueError):
        data = {}
    return data


def set_data(name, data, data_format=ConfigFormat.JSON):
    cfgpath = os.path.join(ROOTDIR, "config", name)
    if data_format == ConfigFormat.JSON:
        with open(cfgpath, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
    elif data_format == ConfigFormat.PICKLE:
        with open(cfgpath, 'wb') as f:
            pickle.dump(data, f)


def get_value(name, var, data_format=ConfigFormat.JSON):
    """
    Read the `var` value from the config for `name`.
    """
    return get_data(name, data_format)[var]


def set_value(name, var, value, data_format=ConfigFormat.JSON):
    """
    Set the `var` value from the config for `name` to `value`.
    """
    data = get_data(name)
    data[var] = value
    set_data(name, data, data_format)
