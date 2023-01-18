from typing import Any, Optional, List, Dict

from pydantic import BaseModel, Field


class Mesajlar(BaseModel):
    hatalar: Any
    uyarilar: Any
    onaylar: Any
    basarilar: Any
    sorular: Any


class Imza(BaseModel):
    imzalanabilir: bool
    rota_gerekli: bool = Field(..., alias='rotaGerekli')
    rota: Any
    degerlendirme_ana_tur: Any = Field(..., alias='degerlendirmeAnaTur')
    imza_kayit_no: Any = Field(..., alias='imzaKayitNo')
    imza_id: Any = Field(..., alias='imzaId')
    imza_adim_id: Any = Field(..., alias='imzaAdimId')
    imza_adimi_tamamlandi: Any = Field(..., alias='imzaAdimiTamamlandi')


class DonusDegerleri(BaseModel):
    devam_edebilir: bool = Field(..., alias='devamEdebilir')


class Result(BaseModel):
    id: Any
    mesajlar: Mesajlar
    imza: Imza
    yeniden_yukle: bool = Field(..., alias='yenidenYukle')
    donus_degerleri: DonusDegerleri = Field(..., alias='donusDegerleri')


class Error(BaseModel):
    pass


class IkametResponse(BaseModel):
    success: bool
    message: str
    result: Optional[Result] = None
    type: Optional[str] = None
    errors: Dict[str,List[str]] = None


class IkametRequest(BaseModel):
    basvuru_no: Optional[str] = Field(None, alias='basvuruNo')
    cep_telefon: Optional[Any] = Field(None, alias='cepTelefon')
    e_posta: Optional[str] = Field(None, alias='ePosta')
    yabanci_kimlik_no: Optional[Any] = Field(None, alias='yabanciKimlikNo')
    pasaport_belge_no: Optional[str] = Field(None, alias='pasaportBelgeNo')
    islem_tur: Optional[int] = Field(None, alias='islemTur')
    captcha_de_text: Optional[str] = Field(None, alias='CaptchaDeText')
    captcha_input_text: Optional[str] = Field(None, alias='CaptchaInputText')
