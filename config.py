from os import environ as env

TELEGRAM_TOKEN = env.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = env.get('TELEGRAM_CHAT_ID', '204339748')

CAPTCHA_TOKEN = env.get('CAPTCHA_TOKEN', '')

APPLICATION_ID = env.get('APPLICATION_ID')
EMAIL = env.get('EMAIL')
PASSPORT_NUMBER = env.get('PASSPORT_NUMBER')
PHONE_NUMBER = env.get('PHONE_NUMBER')

LOG_LEVEL = env.get('LOG_LEVEL')

N_RETRIES = int(env.get('N_RETRIES', 2))