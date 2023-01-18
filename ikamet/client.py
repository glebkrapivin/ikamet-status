import logging
from urllib.parse import urljoin, urlparse, parse_qs

import pydantic
import requests
from bs4 import BeautifulSoup

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

# Example can be seen https://e-ikamet.goc.gov.tr/DefaultCaptcha/Generate?t=test
BAD_CAPTCHA_IMAGE = b'GIF89a\xc8\x00F\x00\xf7\x00\x00\x00\x00\x00\x00\x003\x00\x00f\x00\x00\x99\x00\x00\xcc\x00\x00\xff\x00+\x00\x00+3\x00+f\x00+\x99\x00+\xcc\x00+\xff\x00U\x00\x00U3\x00Uf\x00U\x99\x00U\xcc\x00U\xff\x00\x80\x00\x00\x803\x00\x80f\x00\x80\x99\x00\x80\xcc\x00\x80\xff\x00\xaa\x00\x00\xaa3\x00\xaaf\x00\xaa\x99\x00\xaa\xcc\x00\xaa\xff\x00\xd5\x00\x00\xd53\x00\xd5f\x00\xd5\x99\x00\xd5\xcc\x00\xd5\xff\x00\xff\x00\x00\xff3\x00\xfff\x00\xff\x99\x00\xff\xcc\x00\xff\xff3\x00\x003\x0033\x00f3\x00\x993\x00\xcc3\x00\xff3+\x003+33+f3+\x993+\xcc3+\xff3U\x003U33Uf3U\x993U\xcc3U\xff3\x80\x003\x8033\x80f3\x80\x993\x80\xcc3\x80\xff3\xaa\x003\xaa33\xaaf3\xaa\x993\xaa\xcc3\xaa\xff3\xd5\x003\xd533\xd5f3\xd5\x993\xd5\xcc3\xd5\xff3\xff\x003\xff33\xfff3\xff\x993\xff\xcc3\xff\xfff\x00\x00f\x003f\x00ff\x00\x99f\x00\xccf\x00\xfff+\x00f+3f+ff+\x99f+\xccf+\xfffU\x00fU3fUffU\x99fU\xccfU\xfff\x80\x00f\x803f\x80ff\x80\x99f\x80\xccf\x80\xfff\xaa\x00f\xaa3f\xaaff\xaa\x99f\xaa\xccf\xaa\xfff\xd5\x00f\xd53f\xd5ff\xd5\x99f\xd5\xccf\xd5\xfff\xff\x00f\xff3f\xffff\xff\x99f\xff\xccf\xff\xff\x99\x00\x00\x99\x003\x99\x00f\x99\x00\x99\x99\x00\xcc\x99\x00\xff\x99+\x00\x99+3\x99+f\x99+\x99\x99+\xcc\x99+\xff\x99U\x00\x99U3\x99Uf\x99U\x99\x99U\xcc\x99U\xff\x99\x80\x00\x99\x803\x99\x80f\x99\x80\x99\x99\x80\xcc\x99\x80\xff\x99\xaa\x00\x99\xaa3\x99\xaaf\x99\xaa\x99\x99\xaa\xcc\x99\xaa\xff\x99\xd5\x00\x99\xd53\x99\xd5f\x99\xd5\x99\x99\xd5\xcc\x99\xd5\xff\x99\xff\x00\x99\xff3\x99\xfff\x99\xff\x99\x99\xff\xcc\x99\xff\xff\xcc\x00\x00\xcc\x003\xcc\x00f\xcc\x00\x99\xcc\x00\xcc\xcc\x00\xff\xcc+\x00\xcc+3\xcc+f\xcc+\x99\xcc+\xcc\xcc+\xff\xccU\x00\xccU3\xccUf\xccU\x99\xccU\xcc\xccU\xff\xcc\x80\x00\xcc\x803\xcc\x80f\xcc\x80\x99\xcc\x80\xcc\xcc\x80\xff\xcc\xaa\x00\xcc\xaa3\xcc\xaaf\xcc\xaa\x99\xcc\xaa\xcc\xcc\xaa\xff\xcc\xd5\x00\xcc\xd53\xcc\xd5f\xcc\xd5\x99\xcc\xd5\xcc\xcc\xd5\xff\xcc\xff\x00\xcc\xff3\xcc\xfff\xcc\xff\x99\xcc\xff\xcc\xcc\xff\xff\xff\x00\x00\xff\x003\xff\x00f\xff\x00\x99\xff\x00\xcc\xff\x00\xff\xff+\x00\xff+3\xff+f\xff+\x99\xff+\xcc\xff+\xff\xffU\x00\xffU3\xffUf\xffU\x99\xffU\xcc\xffU\xff\xff\x80\x00\xff\x803\xff\x80f\xff\x80\x99\xff\x80\xcc\xff\x80\xff\xff\xaa\x00\xff\xaa3\xff\xaaf\xff\xaa\x99\xff\xaa\xcc\xff\xaa\xff\xff\xd5\x00\xff\xd53\xff\xd5f\xff\xd5\x99\xff\xd5\xcc\xff\xd5\xff\xff\xff\x00\xff\xff3\xff\xfff\xff\xff\x99\xff\xff\xcc\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\xfc\x00,\x00\x00\x00\x00\xc8\x00F\x00\x00\x08\xff\x00\xa5I\x03@\xb0\xa0\xc1\x83\x08\x13*\\\xc8\xb0\xa1\xc3\x87\x10#J\x9cH\xb1b\xc2\x81\x00\x04b\xb4\xc8\xb1\xa3\xc7\x8f C\x8a\xcc(\x10\xa1\xc6\x91(S\xaa\\\xc9\x92\xe0\xc9\x86/[\xca\x9cISf\xcc\x88%k\xea\xdc\xc9SbN\x8e7{\n\x1d:3\xa8G\xa3D\x93*\xad\x88Td\xd3\xa5P\xa3\xba\xfcI\xf3\xa9\xd4\xab:\xad\x16\xa5\x8a\xb5kK\xad<\xc1z\x1d\xeb\x93+V\xb3d\xd3BD;V\xacZ\xb2n\xbb\xc6}\xbbtnZ\xbbt\xb3\xb2\xcd\xcb\x10/\xdf\x94~\xff\x16\x0c,\xd8"\xe1\xc2\x07\x0f#\xee\xbbw1\xd0\x8d\x8e\x8fB\x8e\x8cRqa\xcb\x94\x1fb\xbe\xdb8\xf3\xca\xcdRA{6\xdc\xf9\xad\xe8\xd1\x1fOo\x9d\x8c\xfa\xaa\xea\xca\xa5[G\x8d\xdd\x93\xb6l\xd7\xb6\xbf\xe6\xbe-ww\xc8\xd7\xbc\x87\x02O\xec;x\xde\xd7\xc3\x8d\xe3f\xcd\xb4\xb8r\xca~\x93?\xa7k\xdb\xf9t\xdeO\xa5__\x1cS\xfb\xf6\xcc\xde\xbfG}\xeen]<\xf6\xbd\xe1\xcd{\x8d\x9b^}]\xe6k\xe1\xbb\xf7\x8c\xb9\xfd|\xdd\xf2;\xda\xbf\xff\xbb<N\xff\xfcU\x05`s\xf9\x05(\xd4~\x17\rh\xe0c\x05\n\xa7\xe0\x82\xf1Q\xd7 \x84\xfa=X\x13\x82\xcfa\xe8\x94\x85\xf3i\xf8\x19\x87\xd7y(\xe0\x84\x01\x8aX\x1b\x88\xe0\xa1\xf8\x97\x89P\xa9\xe8\x98\x8bj\xb1\xd8\x16\x8c\xcbQ\xe8\x90\x8c\x80\xd1\xa8\x1c\x8e\x92\x91h\xe3B<\x96\xe5\xe3\x8f\x9a\xe9\xd8\xdf\x90DN4\x14\xa4AF&IR\x8dN\xee\xe4\xe1\x92\x0b\xb6G%\x91\xc9]\x19\xe5TH\xc2\xd4\xe4\x96 \x1d\xa6%\x98^"\xf9%\x99\xba\xddx&\x9a\xab\x99\xb4&\x9bR\x96\x14\x10\x00;'


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
                          ) -> str:

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
        logging.debug('Reponse: %s', response)

        # No info about the response when the application is actually processed
        # so return NO_RESULT if there is no result_id otherwise the whole result object
        if response.success:
            if not response.result.donus_degerleri:
                raise IkametError('Application not found')
            if not response.result.id:
                return 'NOT_PROCESSED'
            return str(response.result)
        if not response.success:
            raise IkametError(str(response.errors))
