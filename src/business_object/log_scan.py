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
        if not isinstance(id_qrcode, int):
            raise ValueError("id_qrcode doit être un entier.")

        # --- Attributs privés ---
        self.__id_qrcode = id_qrcode
        self.__client_host = client_host
        self.__user_agent = user_agent
        self.__referer = referer
        self.__accept_language = accept_language
        self.__geo_country = geo_country
        self.__geo_region = geo_region
        self.__geo_city = geo_city
        self.__id_scan = id_scan
        self.__date_scan = date_scan

    # --- Propriétés (Getters/Setters) ---

    @property
    def id_scan(self) -> Optional[int]:
        return self.__id_scan

    @id_scan.setter
    def id_scan(self, value: Optional[int]):
        if value is not None and not isinstance(value, int):
            raise ValueError("id_scan doit être un entier ou None.")
        self.__id_scan = value

    @property
    def id_qrcode(self) -> int:
        return self.__id_qrcode

    @id_qrcode.setter
    def id_qrcode(self, value: int):
        if not isinstance(value, int):
            raise ValueError("id_qrcode doit être un entier.")
        self.__id_qrcode = value

    @property
    def date_scan(self) -> Optional[datetime]:
        return self.__date_scan

    @date_scan.setter
    def date_scan(self, value: Optional[datetime]):
        if value is not None and not isinstance(value, datetime):
            raise ValueError("date_scan doit être un datetime ou None.")
        self.__date_scan = value

    @property
    def client_host(self) -> Optional[str]:
        return self.__client_host

    @client_host.setter
    def client_host(self, value: Optional[str]):
        self.__client_host = value

    @property
    def user_agent(self) -> Optional[str]:
        return self.__user_agent

    @user_agent.setter
    def user_agent(self, value: Optional[str]):
        self.__user_agent = value

    @property
    def referer(self) -> Optional[str]:
        return self.__referer

    @referer.setter
    def referer(self, value: Optional[str]):
        self.__referer = value

    @property
    def accept_language(self) -> Optional[str]:
        return self.__accept_language

    @accept_language.setter
    def accept_language(self, value: Optional[str]):
        self.__accept_language = value

    @property
    def geo_country(self) -> Optional[str]:
        return self.__geo_country

    @geo_country.setter
    def geo_country(self, value: Optional[str]):
        self.__geo_country = value

    @property
    def geo_region(self) -> Optional[str]:
        return self.__geo_region

    @geo_region.setter
    def geo_region(self, value: Optional[str]):
        self.__geo_region = value

    @property
    def geo_city(self) -> Optional[str]:
        return self.__geo_city

    @geo_city.setter
    def geo_city(self, value: Optional[str]):
        self.__geo_city = value

    def __repr__(self) -> str:
        return (
            f"LogScan(id_scan={self.__id_scan}, id_qrcode={self.__id_qrcode}, "
            f"date_scan={self.__date_scan}, client_host='{self.__client_host}')"
        )
