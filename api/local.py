from api.db import get_user as db_get_user


class User:
    @staticmethod
    def get_user(user_id: int):
        return db_get_user(user_id)
