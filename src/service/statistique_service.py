from utils.log_decorator import log
from business_object.statistique import Statistique
from dao.statistique_dao import StatistiqueDao

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
        return utilisateurs

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
