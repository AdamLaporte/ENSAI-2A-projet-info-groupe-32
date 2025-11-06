from utils.log_decorator import log
from business_object.statistique import Statistique
from dao.statistique_dao import StatistiqueDao
from datetime import date 
from typing import Dict, Any
from dao.log_scan_dao import LogScanDao


class StatistiqueService:
    """Classe contenant les méthodes de service des Statistiques"""
    
    @log
    def creer_statistique(self, id_qrcode, nombre_vue, date_des_vues) -> Statistique:
        """Création d'une statistique à partir de ses attributs"""
        nouvelle_statistique = Statistique(
            id_qrcode=id_qrcode,
            nombre_vue=nombre_vue,
            date_des_vues=date_des_vues
        )
        return nouvelle_statistique if StatistiqueDao().creer_statistique(nouvelle_statistique) else None

    @log
    def lister_tous(self) -> list[Statistique]:
        """
        Lister toutes les statistiques
        """
        statistiques = StatistiqueDao().lister_tous()
        return statistiques

    @log
    def trouver_par_id_qrcode(self, id_qrcode) -> Statistique:
        """Trouver un utilisateur à partir de son id_qrcode"""
        return StatistiqueDao().trouver_par_id_qrcode(id_qrcode)

    @log
    def modifier_statistique(self, statistique) -> Statistique:
        """Modification d'une statistique"""
        return statistique if StatistiqueDao().modifier_statistique(statistique) else None

    @log
    def supprimer(self, statistique) -> bool:
        """Supprimer une statistique"""
        return StatistiqueDao().supprimer(statistique)

    @log
    def id_qrcode_deja_utilise(self, id_qrcode) -> bool:
        """Vérifie si le id_qrcode est déjà utilisé
        Retourne True si le id_qrcode existe déjà en BDD"""
        statistiques = StatistiqueDao().lister_tous()
        return id_qrcode in [i.id_qrcode for i in statistiques]

    @log
    def enregistrer_vue(self, id_qrcode: int, date_vue: date) -> bool:
        """
        Demande au DAO d'incrémenter le compteur de vues pour un jour donné.
        """
        return StatistiqueDao().incrementer_vue_jour(id_qrcode, date_vue)

    @log
    def get_statistiques_qr_code(self, id_qrcode: int, detail: bool = True) -> Dict[str, Any]:
        """
        Orchestre la récupération des statistiques complètes pour un QR code.
        Appelle les DAOs pour les agrégats, les stats par jour et les logs récents.
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
                {"date": r["date_des_vues"].isoformat(), "vues": int(r["nombre_vue"])}
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