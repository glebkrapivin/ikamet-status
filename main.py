import logging

from captcha_provider import TwoCaptchaProvider
from config import CAPTCHA_TOKEN, TELEGRAM_TOKEN, EMAIL, APPLICATION_ID, PASSPORT_NUMBER, TELEGRAM_CHAT_ID, LOG_LEVEL
from ikamet.client import IkametClient
from notifier import TelegramNotifier

def main():
    client = IkametClient()
    provider = TwoCaptchaProvider(CAPTCHA_TOKEN)
    notifier = TelegramNotifier(TELEGRAM_TOKEN, check_token=True)

    _id, bytes = client.get_captcha()
    logging.info('Downloaded captcha')
    solved_captcha = provider.solve_captcha(bytes)
    logging.info('Solved captcha')
    try:
        result = client.get_ikamet_result(application_id=APPLICATION_ID,
                                          email=EMAIL,
                                          foreign_passport_number=PASSPORT_NUMBER,
                                          captcha_id=_id,
                                          captcha_text=solved_captcha
                                          )
        notifier.send_message(TELEGRAM_CHAT_ID, result)
    except ValueError as e:
        notifier.send_message(TELEGRAM_CHAT_ID, str(e))
    logging.info('Got result, sent to notifier')


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)
    main()


