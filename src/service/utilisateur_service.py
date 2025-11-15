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
        """
        Crée un utilisateur à partir d’un nom d’utilisateur et d’un mot de passe.

        Paramètres
        ----------
        nom_user : str
            Identifiant choisi pour l’utilisateur (login unique).
        mdp : str
            Mot de passe fourni en clair, à hasher lors de la création.

        Retour
        ------
        Utilisateur | None
            - Renvoie l’objet Utilisateur créé (avec id_user renseigné après insertion).
            - Renvoie None si l’insertion en base échoue.

        Notes
        -----
        Le mot de passe est hashé avec nom_user comme sel pour obtenir une
        valeur stable. L’insertion réelle est réalisée via UtilisateurDao().
        """
        hashed = hash_password(mdp, nom_user)
        nouveau = Utilisateur(
            id_user=None,
            nom_user=nom_user,
            mdp=hashed,
        )
        return nouveau if UtilisateurDao().creer_user(nouveau) else None


    @log
    def lister_tous(self, inclure_mdp: bool = False) -> list[Utilisateur]:
        """
        Liste l’ensemble des utilisateurs présents en base.

        Paramètres
        ----------
        inclure_mdp : bool, par défaut False
            Indique s’il faut inclure les mots de passe hashés dans le retour.
            Si False, tous les champs mdp des objets retournés sont mis à None.

        Retour
        ------
        list[Utilisateur]
            Liste d’objets Utilisateur récupérés en base.

        Notes
        -----
        L’accès aux données est délégué à UtilisateurDao(). Le masquage des
        mots de passe est appliqué côté service pour renforcer la sécurité.
        """
        utilisateurs = UtilisateurDao().lister_tous()
        if not inclure_mdp:
            for u in utilisateurs:
                u.mdp = None
        return utilisateurs


    @log
    def trouver_par_id_user(self, id_user: int) -> Utilisateur | None:
        """
        Recherche un utilisateur via son identifiant numérique.

        Paramètres
        ----------
        id_user : int
            Identifiant unique de l’utilisateur recherché.

        Retour
        ------
        Utilisateur | None
            - Renvoie l’utilisateur correspondant si trouvé.
            - Renvoie None si aucun utilisateur ne correspond.

        Notes
        -----
        Le service délègue la recherche à UtilisateurDao().
        """
        return UtilisateurDao().trouver_par_id_user(id_user)


    @log
    def trouver_par_nom_user(self, nom_user: str) -> Utilisateur | None:
        """
        Recherche un utilisateur à partir de son login.

        Paramètres
        ----------
        nom_user : str
            Login (nom d’utilisateur) tel qu’enregistré en base.

        Retour
        ------
        Utilisateur | None
            Utilisateur correspondant ou None si aucun résultat.

        Notes
        -----
        Méthode utile pour les mécanismes d’authentification.
        """
        return UtilisateurDao().trouver_par_nom_user(nom_user)


    @log
    def modifier_user(self, utilisateur: Utilisateur) -> Utilisateur | None:
        """
        Modifie un utilisateur existant.

        Paramètres
        ----------
        utilisateur : Utilisateur
            Objet contenant les nouvelles valeurs à appliquer.
            Si utilisateur.mdp est fourni en clair, il est re-hashé.

        Retour
        ------
        Utilisateur | None
            - Renvoie l’objet mis à jour si la modification réussit.
            - Renvoie None si l’opération échoue (ex. id inexistant).

        Notes
        -----
        Le re-hash du mot de passe utilise nom_user comme sel.
        La mise à jour réelle est effectuée via UtilisateurDao().
        """
        if utilisateur.mdp:
            utilisateur.mdp = hash_password(utilisateur.mdp, utilisateur.nom_user)
        return utilisateur if UtilisateurDao().modifier_user(utilisateur) else None


    @log
    def supprimer(self, utilisateur: Utilisateur) -> bool:
        """
        Supprime un utilisateur existant.

        Paramètres
        ----------
        utilisateur : Utilisateur
            Objet contenant au minimum id_user, utilisé pour la suppression.

        Retour
        ------
        bool
            - True si la suppression a été effectuée,
            - False si l’utilisateur n’existe pas.

        Notes
        -----
        Le service ne réalise aucune vérification supplémentaire.
        L’opération est effectuée par UtilisateurDao().
        """
        return UtilisateurDao().supprimer(utilisateur)


    @log
    def se_connecter(self, nom_user: str, mdp: str) -> Utilisateur | None:
        """
        Authentifie un utilisateur à partir de son login et mot de passe.

        Paramètres
        ----------
        nom_user : str
            Nom d’utilisateur saisi.
        mdp : str
            Mot de passe en clair saisi par l’utilisateur.

        Retour
        ------
        Utilisateur | None
            - Renvoie l’utilisateur si les identifiants sont valides.
            - Renvoie None si l’authentification échoue.

        Notes
        -----
        Le mot de passe fourni est hashé avec nom_user et comparé
        au hash stocké en base.
        """
        return UtilisateurDao().se_connecter(nom_user, hash_password(mdp, nom_user))


    @log
    def nom_user_deja_utilise(self, nom_user: str) -> bool:
        """
        Vérifie si un nom d’utilisateur est déjà pris.

        Paramètres
        ----------
        nom_user : str
            Login à vérifier.

        Retour
        ------
        bool
            - True si le login existe déjà,
            - False sinon.

        Notes
        -----
        La recherche est effectuée en listant tous les utilisateurs.
        Méthode utile pour les opérations de création de compte.
        """
        utilisateurs = UtilisateurDao().lister_tous()
        return nom_user in [u.nom_user for u in utilisateurs]
