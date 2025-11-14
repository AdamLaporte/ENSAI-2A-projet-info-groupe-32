import logging

from utils.singleton import Singleton
from utils.log_decorator import log
from datetime import date, datetime
from dao.db_connection import DBConnection
from typing import List, Dict, Any, Optional
from business_object.statistique import Statistique


class StatistiqueDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Statistiques dans la base de données"""

    @log
    def incrementer_vue_jour(self, id_qrcode: int, date_vue: date) -> bool:
        """
        Incrémente le compteur de vues pour un qrcode à une date donnée.
        Crée la ligne si elle n'existe pas (UPSERT).
        """
        try:
            with DBConnection().connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO statistique (id_qrcode, nombre_vue, date_des_vues)
                        VALUES (%s, 1, %s)
                        ON CONFLICT (id_qrcode, date_des_vues)
                        DO UPDATE SET nombre_vue = statistique.nombre_vue + 1;
                        """,
                        (id_qrcode, date_vue),
                    )
                    # rowcount n'est pas fiable pour ON CONFLICT, 
                    # mais on suppose que l'opération réussit si pas d'exception.
                    return True
        except Exception as e:
            logging.exception(f"Erreur lors de l'incrémentation de la vue : {e}")
            return False

    @log
    def get_agregats(self, id_qrcode: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les agrégats (total, première, dernière vue) pour un QR code.
        """
        try:
            with DBConnection().connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            COALESCE(SUM(nombre_vue), 0) AS total_vues,
                            MIN(date_des_vues) AS premiere_vue,
                            MAX(date_des_vues) AS derniere_vue
                        FROM statistique
                        WHERE id_qrcode = %s
                        """,
                        (id_qrcode,),
                    )
                    # Retourne le dictionnaire de résultats (ou None)
                    return cur.fetchone()
        except Exception as e:
            logging.exception(f"Erreur DAO en récupérant les agrégats stats : {e}")
            return None

    @log
    def get_stats_par_jour(self, id_qrcode: int) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des vues jour par jour pour un QR code.
        """
        try:
            with DBConnection().connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT date_des_vues, nombre_vue
                        FROM statistique
                        WHERE id_qrcode = %s
                        ORDER BY date_des_vues ASC
                        """,
                        (id_qrcode,),
                    )
                    return cur.fetchall() or []
        except Exception as e:
            logging.exception(f"Erreur DAO en récupérant les stats par jour : {e}")
            return []