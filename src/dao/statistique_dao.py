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
        Incrémente le compteur de vues pour un QR code à une date donnée.

        Paramètres
        ----------
        id_qrcode : int
            Identifiant du QR code pour lequel la vue doit être incrémentée.
        date_vue : date
            Date du scan à enregistrer dans la table statistique.

        Retour
        ------
        bool
            - True si l'incrémentation (ou la création de ligne) s'est déroulée sans erreur.
            - False en cas d'échec ou d'exception.

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
            Récupère les agrégats statistiques d’un QR code.

            Paramètres
            ----------
            id_qrcode : int
                Identifiant du QR code dont on souhaite extraire les agrégats.

            Retour
            ------
            Optional[Dict[str, Any]]
                Un dictionnaire contenant :
                - "total_vues" : int
                    Nombre total cumulé de vues.
                - "premiere_vue" : date ou None
                    Date de la toute première vue enregistrée.
                - "derniere_vue" : date ou None
                    Date de la vue la plus récente.
                Renvoie None en cas d’erreur.

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
        Récupère l’historique quotidien des vues pour un QR code.

        Paramètres
        ----------
        id_qrcode : int
            Identifiant du QR code dont on veut obtenir les statistiques journalières.

        Retour
        ------
        List[Dict[str, Any]]
            Une liste ordonnée chronologiquement (ASC) de dictionnaires, chacun contenant :
            - "date_des_vues" : date
                Jour correspondant aux vues enregistrées.
            - "nombre_vue" : int
                Nombre de vues pour ce jour.
            Cette liste est vide si aucune donnée n’est disponible ou en cas d’erreur.

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