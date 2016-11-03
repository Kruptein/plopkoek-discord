import requests

from utils import get_value, API_VERSION

HEADERS = {
    "Authorization": "Bot {}".format(get_value("main", "discord-token")),
    "User-Agent": "DiscordBot (http://darragh.egon.me, 0.1)"
}


def get(url: str):
    r = requests.get('https://discordapp.com/api/v{}{}'.format(API_VERSION, url), headers=HEADERS)
    return r.json()


def post(url: str, data):
    return requests.post('https://discordapp.com/api/v{}{}'.format(API_VERSION, url), json=data, headers=HEADERS)


def patch(url: str, data):
    return requests.patch('https://discordapp.com/api/v{}{}'.format(API_VERSION, url), json=data, headers=HEADERS)


class Gateway:
    @staticmethod
    def get_url():
        return get("/gateway")["url"]


class Channel:
    @staticmethod
    def create_message(channel_id: int, content: str):
        return post("/channels/{}/messages".format(channel_id), {'content': content})


class User:
    @staticmethod
    def modify_current_user(username: str, avatar):
        return patch("/users/@me", {'username': username, 'avatar': 'data:image/jpeg;base64;{}'.format(avatar)})


class Webhook:
    @staticmethod
    def execute_content(webhook_id: int, token: str, content: str, username: str = None, avatar_url: str = None):
        return post("/webhooks/{}/{}".format(webhook_id, token),
                    {'content': content, 'username': username, 'avatar_url': avatar_url})
