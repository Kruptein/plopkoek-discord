from api.cache import get_users
from api.exceptions import NotCachedException


class User:
    @staticmethod
    def get_user(user_id: int):
        try:
            return get_users()[user_id]
        except KeyError:
            raise NotCachedException()
