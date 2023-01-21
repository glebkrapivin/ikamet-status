import logging

from captcha_provider import TwoCaptchaProvider, TwoCaptchaType
from config import CAPTCHA_TOKEN, TELEGRAM_TOKEN, EMAIL, APPLICATION_ID, PASSPORT_NUMBER, TELEGRAM_CHAT_ID, LOG_LEVEL, \
    N_RETRIES
from ikamet.client import IkametClient, IkametError
from notifier import TelegramNotifier, TransportError, TelegramError


def get_result(client: IkametClient, provider: TwoCaptchaProvider):
    _id, bytes = client.get_captcha()
    logging.info('Downloaded captcha')
    solved_captcha = provider.solve_captcha(bytes, TwoCaptchaType.NORMAL)
    logging.info('Solved captcha')
    message = client.get_ikamet_result(application_id=APPLICATION_ID,
                                       email=EMAIL,
                                       foreign_passport_number=PASSPORT_NUMBER,
                                       captcha_id=_id,
                                       captcha_text=solved_captcha
                                       )
    return message


def main():
    client = IkametClient()
    provider = TwoCaptchaProvider(CAPTCHA_TOKEN)
    notifier = TelegramNotifier(TELEGRAM_TOKEN, check_token=True)

    message = ""
    for i in range(1, N_RETRIES + 1):
        logging.info('Starting attempt #%s', i)
        try:
            message = get_result(client, provider)
            break
        # do better error handling than this :)
        except (IkametError, Exception) as e:
            logging.exception('Attempt #%s failed', i)
    try:
        notifier.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('Got result, sent to notifier')
    except (TransportError, TelegramError):
        logging.exception('Failed sending message to Telegram')


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL,
                        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                        )
    main()
