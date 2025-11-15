from utils.log_decorator import log
from business_object.statistique import Statistique
from dao.statistique_dao import StatistiqueDao
from datetime import date 
from typing import Dict, Any
from dao.log_scan_dao import LogScanDao


class StatistiqueService:
    """Classe contenant les méthodes de service des Statistiques"""

    @log
    def enregistrer_vue(self, id_qrcode: int, date_vue: date) -> bool:
        """
        Enregistre une vue pour un QR code à une date donnée.

        Paramètres
        ----------
        id_qrcode : int
            Identifiant du QR code pour lequel incrémenter le compteur.
        date_vue : date
            Jour auquel la vue doit être ajoutée.

        Retour
        ------
        bool
            - True si l’incrémentation a été effectuée avec succès.
            - False en cas d’échec (ex. QR code inexistant).

        Notes
        -----
        Le service délègue directement l’opération au StatistiqueDao
        via la méthode `incrementer_vue_jour`.
        """
        return StatistiqueDao().incrementer_vue_jour(id_qrcode, date_vue)


    @log
    def get_statistiques_qr_code(self, id_qrcode: int, detail: bool = True) -> Dict[str, Any]:
        """
        Récupère l'ensemble des statistiques liées à un QR code.

        Paramètres
        ----------
        id_qrcode : int
            Identifiant du QR code pour lequel récupérer les statistiques.
        detail : bool, par défaut True
            Indique s’il faut inclure :
            - les statistiques journalières,
            - les logs de scans récents.

        Retour
        ------
        Dict[str, Any]
            Dictionnaire contenant :
            - id_qrcode : int
            - total_vues : int
            - premiere_vue : str | None (ISO 8601)
            - derniere_vue : str | None (ISO 8601)
            - par_jour : list[dict] (si detail=True)
            - scans_recents : list[dict] (si detail=True)

        Notes
        -----
        Le service orchestre trois sources de données :
        - StatistiqueDao.get_agregats : statistiques globales.
        - StatistiqueDao.get_stats_par_jour : vues journalières.
        - LogScanDao.get_scans_recents : informations issues des logs.
        
        Les dates sont converties au format ISO 8601 pour assurer une compatibilité
        front-end et API.
        """
        # 1. Récupérer les agrégats (depuis StatistiqueDao)
        stat_dao = StatistiqueDao()
        agg = stat_dao.get_agregats(id_qrcode)
        
        if not agg:
            agg = {"total_vues": 0, "premiere_vue": None, "derniere_vue": None}

        # 2. Construire le résultat de base
        result = {
            "id_qrcode": id_qrcode,
            "total_vues": int(agg.get("total_vues") or 0),
            "premiere_vue": agg.get("premiere_vue").isoformat() if agg.get("premiere_vue") else None,
            "derniere_vue": agg.get("derniere_vue").isoformat() if agg.get("derniere_vue") else None,
        }

        # 3. Si 'detail' est demandé, récupérer les listes
        if detail:
            # 3.1. Stats par jour (depuis StatistiqueDao)
            rows = stat_dao.get_stats_par_jour(id_qrcode)
            result["par_jour"] = [
                {"date": r["date_des_vues"].isoformat(), "vues": int(r.get("nombre_vue", 0))}
                for r in rows
            ]

            # 3.2. Scans récents (depuis LogScanDao)
            log_dao = LogScanDao()
            logs = log_dao.get_scans_recents(id_qrcode)
            result["scans_recents"] = [
                {
                    "timestamp": log["date_scan"].isoformat(),
                    "client": log["client_host"],
                    "user_agent": log["user_agent"],
                    "referer": log["referer"],
                    "language": log["accept_language"],
                    "geo_country": log["geo_country"],
                    "geo_region": log["geo_region"],
                    "geo_city": log["geo_city"]
                }
                for log in logs
            ]
            
        return result
