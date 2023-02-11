import logging
from enum import Enum
from urllib.parse import urljoin, urlparse, parse_qs
import ipdb
import pydantic
import requests
from bs4 import BeautifulSoup

from ikamet.consts import BAD_CAPTCHA_IMAGE
from ikamet.models import IkametRequest, IkametResponse

ACCEPT_HEADER_CAPTCHA_PAGE = 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'

DEFAULT_HEADERS = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://e-ikamet.goc.gov.tr/',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}


class IkametStatus(Enum):
    NOT_PROCESSED = 1
    ACCEPTED = 2 # not used, cant distinguish
    REJECTED = 3 # not used, cant distinguish
    IS_PROCESSED = 4
    UNKNOWN = 5
    FINISHED = 6


class IkametError(Exception):
    pass


class IkametClient:
    HOST = "https://e-ikamet.goc.gov.tr"

    def __init__(self):
        self.r_session = requests.Session()
        self.r_session.headers.update(DEFAULT_HEADERS)

    def _get_uri(self, path: str) -> str:
        return urljoin(self.HOST, path)

    def _get_captcha_uri(self) -> str:
        r = self.r_session.get(self._get_uri('Ikamet/DevamEdenBasvuruGiris'))
        r.raise_for_status()
        captcha_elem = BeautifulSoup(r.content, 'html.parser').find(id='CaptchaImage')
        if not captcha_elem:
            raise IkametError('Element with ID=\"CaptchaImage\" was not found on the page')
        captcha_uri = captcha_elem.get('src')
        if not captcha_uri:
            raise IkametError('Element with ID=\"CaptchaImage\" does not contain src attr')
        return captcha_uri

    def _get_captcha_obj(self, captcha_uri: str) -> bytes:
        headers = {
            "Accept": ACCEPT_HEADER_CAPTCHA_PAGE
        }
        r = self.r_session.get(self._get_uri(captcha_uri), headers=headers)
        r.raise_for_status()
        captcha_obj = r.content
        if captcha_obj == BAD_CAPTCHA_IMAGE:
            raise IkametError('This is no captcha on the image, it is default \"paywall\"')
        return captcha_obj

    def _get_captcha_id_by_path(self, captcha_uri: str) -> str:
        args = parse_qs(urlparse(captcha_uri).query)
        captcha_id = args.get('t')
        if not captcha_id:
            raise IkametError('Cannot parse captcha ID from the given link')
        return captcha_id[0]

    def get_captcha(self) -> (str, bytes):
        captcha_uri = self._get_captcha_uri()
        captcha_id = self._get_captcha_id_by_path(captcha_uri)
        captcha_bytes = self._get_captcha_obj(captcha_uri)
        return captcha_id, captcha_bytes

    def get_ikamet_result(self,
                          application_id: str,
                          captcha_id: str,
                          captcha_text: str,
                          phone_number: str = None,
                          email: str = None,
                          foreign_passport_number: str = None,
                          turkish_id_number: str = None,
                          ) -> IkametStatus:

        if not ((phone_number and not email) or (not phone_number and email)):
            raise IkametError('Provide number or email')
        if not ((foreign_passport_number and not turkish_id_number) or (
                not foreign_passport_number and turkish_id_number)):
            raise IkametError('Provide foreign passport or turkish id')

        request_data = IkametRequest(basvuru_no=application_id, cep_telefon=phone_number, e_posta=email,
                                     yabanci_kimlik_no=turkish_id_number, pasaport_belge_no=foreign_passport_number,
                                     islem_tur=-1, captcha_de_text=captcha_id, captcha_input_text=captcha_text)
        logging.debug('Request: %s', request_data.dict(by_alias=True))
        r = self.r_session.post(
            urljoin(self.HOST, 'Ikamet/DevamEdenBasvuruGiris/Ara'),
            json=request_data.dict(by_alias=True)
        )
        r.raise_for_status()
        try:
            response: IkametResponse = IkametResponse.parse_raw(r.content)
        except pydantic.ValidationError:
            raise IkametError('Unknown response from website')

        if response.success:
            if not response.result.donus_degerleri:
                raise IkametError('Application not found')
        if not response.success:
            raise IkametError(str(response.errors))

        r = self.r_session.get(self._get_uri('Ikamet/DevamEdenBasvuruGiris'))
        if 'BasvuruDurum' not in r.url:
            return IkametStatus.NOT_PROCESSED
        return IkametStatus.FINISHED
