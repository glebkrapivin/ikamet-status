from abc import abstractmethod
from twocaptcha import TwoCaptcha
from tempfile import NamedTemporaryFile


class BaseCaptchaProvider:

    @abstractmethod
    def solve_captcha(self, bytes: bytes) -> str:
        pass


class TwoCaptchaProvider(TwoCaptcha, BaseCaptchaProvider):

    def __init__(self, apiKey):
        super().__init__(apiKey)

    def solve_captcha(self, bytes: bytes) -> str:
        # TODO: not only gif possible, but twocaptcha guesses based on
        # file extension
        f = NamedTemporaryFile(suffix='.gif')
        f.write(bytes)
        f.flush()
        response = self.normal(f.name)
        return response["code"].upper()