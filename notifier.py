import requests


class TelegramNotifier:

    def __init__(self, bot_token: str):
        self.token = bot_token

    def send_message(self, chat_id: str, text: str):
        data = {
            "chat_id": chat_id,
            "text": text
        }
        r = requests.post(
            url='https://api.telegram.org/bot{0}/sendMessage'.format(self.token),
            data=data
        )
        r.raise_for_status()
        try:
            rj = r.json()
        except:
            rj = {}
        if not rj.get("ok"):
            return ValueError('Failed to send message')

