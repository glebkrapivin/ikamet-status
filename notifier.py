from urllib.parse import urljoin

import requests


class TelegramNotifier:
    HOST = "https://api.telegram.org/"

    def __init__(self, bot_token: str, check_token: bool = False):
        self.token = bot_token
        self.uri = self.HOST + f'bot{self.token}'
        if check_token:
            self.get_me()

    def get_me(self):
        r = requests.get(url=urljoin(self.uri, 'getMe'))
        r.raise_for_status()
        r = r.json()
        if not r["ok"]:
            if r["error_code"] == 401:
                raise ValueError('Wrong Token')
            raise ValueError(r["error_code"])

    def send_message(self, chat_id: str, text: str):
        data = {
            "chat_id": chat_id,
            "text": text
        }
        r = requests.post(
            url=urljoin(self.uri, 'sendMessage'),
            data=data
        )
        r.raise_for_status()
        r = r.json()
        if not r["ok"]:
            return ValueError('Failed to send message')
