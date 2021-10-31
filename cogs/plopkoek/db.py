from datetime import datetime
from api import db


def init_db():
    """
    Initialize the plopkoek database with the PlopkoekTransfer table if no existing table is found.
    """
    conn = db.get_conn()
    # User table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS PlopkoekTransfer("
        "user_from_id TEXT(64) NOT NULL,"
        "user_to_id TEXT(64) NOT NULL,"
        "channel_id TEXT(64) NOT NULL,"
        "message_id TEXT(64) NOT NULL,"
        "dt TIMESTAMP NOT NULL,"
        "FOREIGN KEY(user_from_id) REFERENCES User(user_id),"
        "FOREIGN KEY(user_to_id) REFERENCES User(user_id));"
    )
    conn.close()


def get_income(user_id, fmt):
    conn = db.get_conn()
    count = conn.execute(
        "SELECT COUNT(*) AS count FROM PlopkoekTransfer WHERE "
        "strftime(?, datetime(dt)) == strftime(?, 'now') AND "
        "user_to_id == ?;",
        (
            fmt,
            fmt,
            user_id,
        ),
    ).fetchone()
    conn.close()
    return count["count"]


def get_total_income(user_id):
    conn = db.get_conn()
    count = conn.execute(
        "SELECT COUNT(*) AS count FROM PlopkoekTransfer WHERE user_to_id == ?;",
        (user_id,),
    ).fetchone()["count"]
    conn.close()
    return count


def get_donations_left(user_id):
    conn = db.get_conn()
    count = conn.execute(
        "SELECT COUNT(*) As count FROM PlopkoekTransfer WHERE date(dt) == date('now') AND user_from_id==?;",
        (user_id,),
    ).fetchone()
    conn.close()
    return 5 - count["count"]


def insert_plopkoek(donator_id, receiver_id, channel_id, message_id):
    conn = db.get_conn()
    conn.execute(
        "INSERT INTO PlopkoekTransfer(user_from_id, user_to_id, channel_id, message_id, dt) VALUES (?, ?, ?, ?, ?)",
        (donator_id, receiver_id, channel_id, message_id, datetime.now()),
    )
    conn.commit()
    conn.close()


def delete_plopkoek(donator_id, receiver_id, channel_id, message_id):
    conn = db.get_conn()
    conn.execute(
        "DELETE FROM PlopkoekTransfer "
        "WHERE user_to_id==? AND user_from_id==? AND channel_id=? AND message_id=?",
        (receiver_id, donator_id, channel_id, message_id),
    )
    conn.commit()
    conn.close()


def has_donated_plopkoek(donator_id, receiver_id, channel_id, message_id) -> bool:
    conn = db.get_conn()
    count = conn.execute(
        "SELECT COUNT(*) AS count FROM PlopkoekTransfer "
        "WHERE user_to_id==? AND user_from_id==? AND channel_id=? AND message_id=?",
        (receiver_id, donator_id, channel_id, message_id),
    ).fetchone()["count"]
    conn.close()
    return count > 0


def get_month_ranking(month=None, year=None):
    if not month:
        month = str(datetime.utcnow().month)
    if not year:
        year = str(datetime.utcnow().year)
    if len(month) == 1:
        month = "0" + month

    conn = db.get_conn()
    received_data = conn.execute(
        "SELECT user_to_id, COUNT(user_to_id) AS received "
        "FROM PlopkoekTransfer "
        "WHERE strftime('%m', datetime(dt)) == ? AND "
        "strftime('%Y', datetime(dt)) == ? "
        "GROUP BY user_to_id",
        (month, year),
    ).fetchall()

    donated_data = conn.execute(
        "SELECT user_from_id, COUNT(user_from_id) AS donated "
        "FROM PlopkoekTransfer "
        "WHERE strftime('%m', datetime(dt)) == ? AND "
        "strftime('%Y', datetime(dt)) == ? "
        "GROUP BY user_from_id",
        (month, year),
    ).fetchall()
    conn.close()
    return received_data, donated_data


def get_alltime_ranking():
    conn = db.get_conn()
    received_data = conn.execute(
        "SELECT user_to_id, COUNT(user_to_id) AS received "
        "FROM PlopkoekTransfer "
        "GROUP BY user_to_id"
    ).fetchall()

    donated_data = conn.execute(
        "SELECT user_from_id, COUNT(user_from_id) AS donated "
        "FROM PlopkoekTransfer "
        "GROUP BY user_from_id"
    ).fetchall()
    conn.close()
    return received_data, donated_data
