# src/dao/log_scan_dao.py
import logging
from utils.singleton import Singleton
from utils.log_decorator import log
from dao.db_connection import DBConnection
from business_object.log_scan import LogScan
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LogScanDao(metaclass=Singleton):
    """DAO pour la table logs_scan."""

    @log
    def creer_log(self, log_scan: LogScan) -> bool:
        """
        Insère un objet LogScan dans la base de données.
        'date_scan' utilise DEFAULT NOW() de la BDD.
        """
        try:
            with DBConnection().connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO logs_scan (
                            id_qrcode, client_host, user_agent, referer, accept_language,
                            geo_country, geo_region, geo_city
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id_scan;
                        """,
                        (
                            log_scan.id_qrcode,
                            log_scan.client_host,
                            log_scan.user_agent,
                            log_scan.referer,
                            log_scan.accept_language,
                            log_scan.geo_country,
                            log_scan.geo_region,
                            log_scan.geo_city
                        )
                    )
                    res = cur.fetchone()
                    
                    if res and res.get('id_scan'):
                        log_scan.id_scan = res['id_scan']
                        return True
                    return False
        except Exception as e:
            logger.exception(f"Erreur lors de la création du log de scan : {e}")
            return False

    @log
    def get_scans_recents(self, id_qrcode: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les logs de scan les plus récents pour un QR code.
        """
        try:
            with DBConnection().connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT date_scan, client_host, user_agent, referer, accept_language,
                               geo_country, geo_region, geo_city
                        FROM logs_scan
                        WHERE id_qrcode = %s
                        ORDER BY date_scan DESC
                        LIMIT %s
                        """, 
                        (id_qrcode, limit),
                    )
                    return cur.fetchall() or []
        except Exception as e:
            logging.exception(f"Erreur DAO en récupérant les scans récents : {e}")
            return []