from urllib.parse import urljoin

import requests


class TelegramError(Exception):
    pass


class TransportError(Exception):
    pass


class TelegramNotifier:
    HOST = "https://api.telegram.org/"

    def __init__(self, bot_token: str, check_token: bool = False):
        if not bot_token:
            raise TelegramError('No token')
        self.token = bot_token
        self.uri = self.HOST + f'bot{self.token}/'
        if check_token:
            self.get_me()

    def get_me(self):
        r = requests.get(url=urljoin(self.uri, 'getMe'))
        if r.status_code != 200:
            raise TransportError(r.status_code)
        r = r.json()
        if not r["ok"]:
            if r["error_code"] == 401:
                raise TelegramError('Wrong Token')
            raise TelegramError(r["error_code"])

    def send_message(self, chat_id: str, text: str, silent: bool = False):
        data = {
            "chat_id": chat_id,
            "text": text
        }
        if silent:
            data["disable_notification"] = True
        r = requests.post(
            url=urljoin(self.uri, 'sendMessage'),
            data=data
        )
        if r.status_code != 200:
            raise TransportError(r.status_code)
        r = r.json()
        if not r["ok"]:
            return TelegramError('Failed to send message')
