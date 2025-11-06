# src/business_object/log_scan.py
from datetime import datetime
from typing import Optional

class LogScan:
    """
    Classe métier représentant un enregistrement de scan (log).
    """
    def __init__(
        self,
        id_qrcode: int,
        client_host: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        accept_language: Optional[str] = None,
        geo_country: Optional[str] = None,
        geo_region: Optional[str] = None,
        geo_city: Optional[str] = None,
        id_scan: Optional[int] = None,
        date_scan: Optional[datetime] = None
    ):
        # Validation basique (peut être étendue si nécessaire)
        if not isinstance(id_qrcode, int):
            raise ValueError("id_qrcode doit être un entier.")
            
        self._id_qrcode = id_qrcode
        self._client_host = client_host
        self._user_agent = user_agent
        self._referer = referer
        self._accept_language = accept_language
        self._geo_country = geo_country
        self._geo_region = geo_region
        self._geo_city = geo_city
        self._id_scan = id_scan
        self._date_scan = date_scan

    # --- Propriétés (Getters/Setters) ---

    @property
    def id_scan(self) -> Optional[int]:
        return self._id_scan

    @id_scan.setter
    def id_scan(self, value: Optional[int]):
        if value is not None and not isinstance(value, int):
            raise ValueError("id_scan doit être un entier ou None.")
        self._id_scan = value

    @property
    def id_qrcode(self) -> int:
        return self._id_qrcode

    @id_qrcode.setter
    def id_qrcode(self, value: int):
        if not isinstance(value, int):
            raise ValueError("id_qrcode doit être un entier.")
        self._id_qrcode = value

    @property
    def date_scan(self) -> Optional[datetime]:
        return self._date_scan

    @date_scan.setter
    def date_scan(self, value: Optional[datetime]):
        if value is not None and not isinstance(value, datetime):
            raise ValueError("date_scan doit être un datetime ou None.")
        self._date_scan = value

    @property
    def client_host(self) -> Optional[str]:
        return self._client_host

    @client_host.setter
    def client_host(self, value: Optional[str]):
        self._client_host = value

    @property
    def user_agent(self) -> Optional[str]:
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: Optional[str]):
        self._user_agent = value

    @property
    def referer(self) -> Optional[str]:
        return self._referer

    @referer.setter
    def referer(self, value: Optional[str]):
        self._referer = value

    @property
    def accept_language(self) -> Optional[str]:
        return self._accept_language

    @accept_language.setter
    def accept_language(self, value: Optional[str]):
        self._accept_language = value

    @property
    def geo_country(self) -> Optional[str]:
        return self._geo_country

    @geo_country.setter
    def geo_country(self, value: Optional[str]):
        self._geo_country = value

    @property
    def geo_region(self) -> Optional[str]:
        return self._geo_region

    @geo_region.setter
    def geo_region(self, value: Optional[str]):
        self._geo_region = value

    @property

    def geo_city(self) -> Optional[str]:
        return self._geo_city

    @geo_city.setter
    def geo_city(self, value: Optional[str]):
        self._geo_city = value

    def __repr__(self) -> str:
        return (
            f"LogScan(id_scan={self._id_scan}, id_qrcode={self._id_qrcode}, "
            f"date_scan={self._date_scan}, client_host='{self._client_host}')"
        )