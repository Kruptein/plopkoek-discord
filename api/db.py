import sqlite3

from api.exceptions import NotCachedException


def __get_conn():
    conn = sqlite3.connect("plopkoek.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_basic_discord_cache():
    conn = __get_conn()
    # User table
    conn.execute("CREATE TABLE IF NOT EXISTS User(user_id TEXT(64) PRIMARY KEY UNIQUE NOT NULL, name TEXT NOT NULL);")
    # Guild table
    conn.execute("CREATE TABLE IF NOT EXISTS Guild(guild_id TEXT(64) PRIMARY KEY UNIQUE NOT NULL, name TEXT NOT NULL);")
    # Channel table
    conn.execute("CREATE TABLE IF NOT EXISTS Channel(channel_id TEXT(64) PRIMARY KEY UNIQUE NOT NULL, name TEXT NOT NULL);")
    conn.close()


def update_user(data):
    snowflake = data['id']
    name = data['username']
    conn = __get_conn()
    try:
        user_data = get_user(snowflake)
    except NotCachedException:
        conn.execute("INSERT INTO User (user_id, name) VALUES (?, ?)", (snowflake, name))
        conn.commit()
    else:
        # noinspection PyTypeChecker
        if user_data['name'] != name:
            conn.execute("UPDATE User SET name=? WHERE user_id=?", (name, snowflake))
            conn.commit()


def get_user(user_id):
    conn = __get_conn()
    user_data = conn.execute("SELECT user_id, name FROM User WHERE user_id=?", (user_id,)).fetchone()
    if not user_data:
        raise NotCachedException()
    return user_data


def update_guild(data):
    snowflake = data['id']
    name = data['name']
    conn = __get_conn()
    try:
        guild_data = get_guild(snowflake)
    except NotCachedException:
        conn.execute("INSERT INTO Guild (guild_id, name) VALUES (?, ?)", (snowflake, name))
        conn.commit()
    else:
        # noinspection PyTypeChecker
        if guild_data['name'] != name:
            conn.execute("UPDATE Guild SET name=? WHERE guild_id=?", (name, snowflake))
            conn.commit()


def get_guild(guild_id):
    conn = __get_conn()
    guild_data = conn.execute("SELECT guild_id, name FROM Guild WHERE guild_id=?", (guild_id,)).fetchone()
    if not guild_data:
        raise NotCachedException()
    return guild_data


def remove_guild(data):
    print("Guild remove not yet implemented")


def update_channel(data):
    snowflake = data['id']
    name = data['name']
    conn = __get_conn()
    try:
        channel_data = get_user(snowflake)
    except NotCachedException:
        conn.execute("INSERT INTO Channel (channel_id, name) VALUES (?, ?)", (snowflake, name))
        conn.commit()
    else:
        # noinspection PyTypeChecker
        if channel_data['name'] != name:
            conn.execute("UPDATE Channel SET name=? WHERE channel_id=?", (name, snowflake))
            conn.commit()


def get_channel(channel_id):
    conn = __get_conn()
    channel_data = conn.execute("SELECT channel_id, name FROM Channel WHERE channel_id=?", (channel_id,)).fetchone()
    if not channel_data:
        raise NotCachedException()
    return channel_data


def remove_channel(data):
    print("Channel remove not yet implemented")
