# src/service/log_scan_service.py
from utils.log_decorator import log
from business_object.log_scan import LogScan
from dao.log_scan_dao import LogScanDao
from typing import Optional

class LogScanService:
    """Service pour la gestion des logs de scan."""

    def __init__(self, dao: LogScanDao = LogScanDao()):
        self.dao = dao

    @log
    def enregistrer_log(
        self,
        id_qrcode: int,
        client_host: Optional[str],
        user_agent: Optional[str],
        referer: Optional[str],
        accept_language: Optional[str],
        geo_country: Optional[str],
        geo_region: Optional[str],
        geo_city: Optional[str]
    ) -> Optional[LogScan]:
        """
        Crée un objet LogScan et demande au DAO de l'enregistrer.
        """
        try:
            log_scan = LogScan(
                id_qrcode=id_qrcode,
                client_host=client_host,
                user_agent=user_agent,
                referer=referer,
                accept_language=accept_language,
                geo_country=geo_country,
                geo_region=geo_region,
                geo_city=geo_city
            )
            
            success = self.dao.creer_log(log_scan)
            
            return log_scan if success else None
            
        except Exception as e:
            logging.exception(f"Erreur dans LogScanService : {e}")
            return None