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

#à partir d'ici

#    @log
#    def trouver_par_id_user(self, id_user) -> Utilisateur:
#        """Trouver un utilisateur à partir de son id_user"""
#        return UtilisateurDao().trouver_par_id_user(id_user)

    @log
    def modifier_statistique(self, statistique) -> Statistique:
        """Modification d'une statistique"""
        utilisateur.mdp = hash_password(utilisateur.mdp, utilisateur.id_user)
        return utilisateur if UtilisateurDao().modifier_user(utilisateur) else None

    @log
    def supprimer(self, utilisateur) -> bool:
        """Supprimer le compte d'un utilisateur"""
        return UtilisateurDao().supprimer(utilisateur)

    @log
    def se_connecter(self, pseudo, mdp) -> Utilisateur:
        """Se connecter à partir de pseudo et mdp"""
        return UtilisateurDao().se_connecter(pseudo, hash_password(mdp, pseudo))

    @log
    def id_user_deja_utilise(self, id_user) -> bool:
        """Vérifie si le id_user est déjà utilisé
        Retourne True si le id_user existe déjà en BDD"""
        utilisateurs = UtilisateurDao().lister_tous()
        return id_user in [i.id_user for i in utilisateurs]
