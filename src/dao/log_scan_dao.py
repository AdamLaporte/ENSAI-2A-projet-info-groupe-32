import logging
from typing import Any, Dict, List

from business_object.log_scan import LogScan
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton

logger = logging.getLogger(__name__)


class LogScanDao(metaclass=Singleton):
    """DAO pour la table logs_scan."""

    @log
    def creer_log(self, log: LogScan) -> bool:
        """
        Insère un nouveau log de scan dans la base de données.
        """
        try:
            with DBConnection().connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO logs_scan (
                            id_qrcode, client_host, user_agent, referer, 
                            accept_language, geo_country, geo_region, geo_city, date_scan
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        RETURNING id_scan, date_scan;
                        """,
                        (
                            log.id_qrcode,
                            log.client_host,
                            log.user_agent,
                            log.referer,
                            log.accept_language,
                            log.geo_country,
                            log.geo_region,
                            log.geo_city,
                        ),
                    )
                    res = cur.fetchone()
                    if res:
                        if isinstance(res, dict):
                            log.id_scan = res["id_scan"]
                            log.date_scan = res["date_scan"]
                        else:
                            log.id_scan = res[0]
                            log.date_scan = res[1]
                        return True
            return False

        except Exception as e:
            logger.exception(f"Erreur DAO lors de la création du log : {e}")
            return False

    @log
    def get_scans_recents(self, id_qrcode: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les derniers scans pour un QR code donné.

        Paramètres
        ----------
        id_qrcode : int
            L'identifiant du QR code.
        limit : int
            Nombre maximum de logs à retourner (par défaut 50).

        Retour
        ------
        List[Dict]
            Liste de dictionnaires représentant les logs.
        """
        try:
            with DBConnection().connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT client_host, user_agent, date_scan, referer, 
                               accept_language, geo_country, geo_region, geo_city
                        FROM logs_scan
                        WHERE id_qrcode = %s
                        ORDER BY date_scan DESC
                        LIMIT %s;
                        """,
                        (id_qrcode, limit),
                    )
                    rows = cur.fetchall()

            return rows if rows else []

        except Exception as e:
            logger.exception(f"Erreur DAO lors de la récupération des scans récents : {e}")
            return []
