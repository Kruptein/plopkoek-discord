from api import db


class User:
    @staticmethod
    def get_user(user_id: int):
        return db.get_user(user_id)
