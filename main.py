from twocaptcha import TwoCaptcha

from ikamet.client import IkametClient
from notifier import TelegramNotifier

if __name__ == '__main__':
    client = IkametClient()
    solver = TwoCaptcha('ABCDEF')
    notifier = TelegramNotifier('TOKEN')

    _id, bytes = client.get_captcha()
    solved_captcha = solver.normal(bytes)

    try:
        result = client.get_ikamet_result(application_id='12345', phone_number='124', foreign_passport_number='1234',
                                          captcha_id=_id, captcha_text=solved_captcha)
        notifier.send_message("12345", result)
    except ValueError as e:
        notifier.send_message("12345", str(e))
