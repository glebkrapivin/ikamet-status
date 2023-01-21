from abc import abstractmethod
from enum import Enum
from tempfile import NamedTemporaryFile

from twocaptcha import TwoCaptcha


class TwoCaptchaType(Enum):
    NORMAL = 1


class BaseCaptchaProvider:

    @abstractmethod
    def solve_captcha(self, bytes: bytes, captcha_type: Enum) -> str:
        pass


class TwoCaptchaProvider(TwoCaptcha, BaseCaptchaProvider):

    def __init__(self, apiKey):
        super().__init__(apiKey)

    def solve_captcha(self, bytes: bytes, captcha_type: TwoCaptchaType) -> str:
        if captcha_type != TwoCaptchaType.NORMAL:
            raise NotImplemented("")
        # TODO: not only gif possible, but twocaptcha guesses based on
        # file extension
        f = NamedTemporaryFile(suffix='.gif')
        f.write(bytes)
        f.flush()
        response = self.normal(f.name)
        return response["code"].upper()
