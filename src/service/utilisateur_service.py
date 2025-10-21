from utils.log_decorator import log
from utils.securite import hash_password
from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao


class UtilisateurService:
    """Classe contenant les méthodes de service des Utilisateurs
       Nouveau contrat: id_user = int (PK), nom_user = str (login)
    """

    @log
    def creer_user(self, nom_user: str, mdp: str) -> Utilisateur | None:
        """Création d'un utilisateur à partir de son nom_user et mdp
           - id_user est auto-généré en BDD
           - hash basé sur nom_user pour stabilité
        """
        hashed = hash_password(mdp, nom_user)
        nouveau = Utilisateur(
            id_user=None,           # sera rempli par le DAO (RETURNING id_user)
            nom_user=nom_user,
            mdp=hashed,
        )
        return nouveau if UtilisateurDao().creer_user(nouveau) else None

    @log
    def lister_tous(self, inclure_mdp: bool = False) -> list[Utilisateur]:
        """Lister tous les utilisateurs; masque les mdp par défaut"""
        utilisateurs = UtilisateurDao().lister_tous()
        if not inclure_mdp:
            for u in utilisateurs:
                u.mdp = None
        return utilisateurs

    @log
    def trouver_par_id_user(self, id_user: int) -> Utilisateur | None:
        """Trouver un utilisateur par id_user (entier)"""
        return UtilisateurDao().trouver_par_id_user(id_user)

    @log
    def trouver_par_nom_user(self, nom_user: str) -> Utilisateur | None:
        """Trouver un utilisateur par nom_user (login)"""
        return UtilisateurDao().trouver_par_nom_user(nom_user)

    @log
    def modifier_user(self, utilisateur: Utilisateur) -> Utilisateur | None:
        """Modifier un utilisateur; re-hash si mdp fourni en clair
           Convention: si utilisateur.mdp est déjà hashé, ne pas le ré‑hasher
           Ici, on choisit de re‑hasher si un mdp non vide est fourni.
        """
        if utilisateur.mdp:
            # saler avec nom_user (stable) plutôt que id_user
            utilisateur.mdp = hash_password(utilisateur.mdp, utilisateur.nom_user)
        return utilisateur if UtilisateurDao().modifier_user(utilisateur) else None

    @log
    def supprimer(self, utilisateur: Utilisateur) -> bool:
        """Supprimer le compte d'un utilisateur"""
        return UtilisateurDao().supprimer(utilisateur)

    @log
    def se_connecter(self, nom_user: str, mdp: str) -> Utilisateur | None:
        """Connexion par nom_user + mdp (hash avec nom_user)"""
        return UtilisateurDao().se_connecter(nom_user, hash_password(mdp, nom_user))

    @log
    def nom_user_deja_utilise(self, nom_user: str) -> bool:
        """Vérifie si le nom_user est déjà utilisé"""
        utilisateurs = UtilisateurDao().lister_tous()
        return nom_user in [u.nom_user for u in utilisateurs]
