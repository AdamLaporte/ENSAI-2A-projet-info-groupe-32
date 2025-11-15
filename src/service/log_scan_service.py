# src/service/log_scan_service.py
from utils.log_decorator import log
from business_object.log_scan import LogScan
from dao.log_scan_dao import LogScanDao
from typing import Optional
import logging




class LogScanService:
    """Service pour la gestion des logs de scan."""

    def __init__(self, dao: LogScanDao = LogScanDao()):
        self.dao = dao

    @log
    def enregistrer_log(
    self,
    id_qrcode: int,
    client_host: Optional[str] = None,
    user_agent: Optional[str] = None,
    referer: Optional[str] = None,
    accept_language: Optional[str] = None,
    geo_country: Optional[str] = None,
    geo_region: Optional[str] = None,
    geo_city: Optional[str] = None
) -> Optional[LogScan]:
        """
        Enregistre un log de scan pour un QR code.

        Paramètres
        ----------
        id_qrcode : int
            Identifiant du QR code scanné.
        client_host : str, optionnel
            Adresse IP du client ayant effectué le scan.
        user_agent : str, optionnel
            User-Agent du client (navigateur ou application).
        referer : str, optionnel
            URL de provenance du scan.
        accept_language : str, optionnel
            Chaîne indiquant la langue préférée du client.
        geo_country : str, optionnel
            Pays déduit de la géolocalisation.
        geo_region : str, optionnel
            Région déduite de la géolocalisation.
        geo_city : str, optionnel
            Ville déduite de la géolocalisation.

        Retour
        ------
        Optional[LogScan]
            - Renvoie l’objet LogScan créé et enregistré en base si succès.
            - Renvoie None si l’enregistrement échoue ou en cas d’erreur.

        Notes
        -----
        - L’objet LogScan est construit dans le service, puis transmis au DAO.
        - Toute exception interne est interceptée et journalisée ; la méthode
        renvoie alors None pour ne jamais interrompre le flux d’exécution.
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
