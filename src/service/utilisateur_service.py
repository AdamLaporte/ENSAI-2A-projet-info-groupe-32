from utils.log_decorator import log
from utils.securite import hash_password
from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao

class UtilisateurService:
    """Classe contenant les méthodes de service des Utilisateurs"""
    
    @log
    def creer_user(self, id_user, mdp) -> Utilisateur:
        """Création d'un utilisateur à partir de ses attributs"""
        nouveau_utilisateur = Utilisateur(
            id_user=id_user,
            mdp=hash_password(mdp, id_user),
        )
        return nouveau_utilisateur if UtilisateurDao().creer_user(nouveau_utilisateur) else None

    @log
    def lister_tous(self, inclure_mdp=False) -> list[Utilisateur]:
        """Lister tous les utilisateurs
        Si inclure_mdp=True, les mots de passe seront inclus
        Par défaut, tous les mdp des utilisateurs sont à None
        """
        utilisateurs = UtilisateurDao().lister_tous()
        if not inclure_mdp:
            for i in utilisateurs:
                i.mdp = None
        return utilisateurs

    @log
    def trouver_par_id_user(self, id_user) -> Utilisateur:
        """Trouver un utilisateur à partir de son id_user"""
        return UtilisateurDao().trouver_par_id_user(id_user)

    @log
    def modifier_user(self, utilisateur) -> Utilisateur:
        """Modification d'un utilisateur"""
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
