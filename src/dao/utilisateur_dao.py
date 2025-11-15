import logging

from utils.singleton import Singleton
from utils.log_decorator import log
from dao.db_connection import DBConnection
from business_object.utilisateur import Utilisateur


class UtilisateurDao(metaclass=Singleton):
    """Accès aux Utilisateurs en BDD (id_user: int PK, nom_user: str)"""

    @log
    def creer_user(self, utilisateur: Utilisateur) -> bool:
        """
        Crée un nouvel utilisateur en base.

        Paramètres
        ----------
        utilisateur : Utilisateur
            Objet métier contenant :
            - nom_user : str (login)
            - mdp : str (mot de passe déjà hashé)
            L’attribut id_user doit être None avant insertion.

        Retour
        ------
        bool
            - True si l’insertion s’est déroulée correctement (id_user rempli).
            - False en cas d’erreur ou d’échec d’insertion.

        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO utilisateur (nom_user, mdp)
                        VALUES (%(nom_user)s, %(mdp)s)
                        RETURNING id_user;
                        """,
                        {
                            "nom_user": utilisateur.nom_user,
                            "mdp": utilisateur.mdp,
                        },
                    )
                    row = cursor.fetchone()
                    if row:
                        # selon le cursor_factory (DictCursor ou non)
                        utilisateur.id_user = row["id_user"] if isinstance(row, dict) else row[0]
                        res = True
        except Exception as e:
            logging.info(e)
            res = False
        return bool(res)

    @log
    def trouver_par_id_user(self, id_user: int) -> Utilisateur | None:
        """
        Recherche un utilisateur à partir de son identifiant unique.

        Paramètres
        ----------
        id_user : int
            Identifiant numérique du compte utilisateur recherché.

        Retour
        ------
        Utilisateur | None
            - L’objet utilisateur correspondant si trouvé.
            - None si aucun utilisateur ne correspond à l’identifiant.

        Notes
        -----
        - Supporte dict ou tuple selon le curseur.
        - Lève l’exception SQL en cas d’erreur (logging + raise).
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id_user, nom_user, mdp
                          FROM utilisateur
                         WHERE id_user = %(id_user)s;
                        """,
                        {"id_user": id_user},
                    )
                    row = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        if not row:
            return None

        return Utilisateur(
            id_user=row["id_user"] if isinstance(row, dict) else row[0],
            nom_user=row["nom_user"] if isinstance(row, dict) else row[1],
            mdp=row["mdp"] if isinstance(row, dict) else row[2],
        )

    @log
    def trouver_par_nom_user(self, nom_user: str) -> Utilisateur | None:
        """
        Recherche un utilisateur par son nom d’utilisateur (login).

        Paramètres
        ----------
        nom_user : str
            Login de l’utilisateur à rechercher.

        Retour
        ------
        Utilisateur | None
            - L’objet utilisateur si trouvé.
            - None si aucun utilisateur ne correspond.

        
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id_user, nom_user, mdp
                          FROM utilisateur
                         WHERE nom_user = %(nom_user)s;
                        """,
                        {"nom_user": nom_user},
                    )
                    row = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        if not row:
            return None

        return Utilisateur(
            id_user=row["id_user"] if isinstance(row, dict) else row[0],
            nom_user=row["nom_user"] if isinstance(row, dict) else row[1],
            mdp=row["mdp"] if isinstance(row, dict) else row[2],
        )

    @log
    def lister_tous(self) -> list[Utilisateur]:
        """
        Liste l’ensemble des utilisateurs enregistrés en base.

        Paramètres
        ----------
        Aucun

        Retour
        ------
        list[Utilisateur]
            Liste d’objets Utilisateur, triée par id_user croissant.
            Liste vide si aucun utilisateur n’existe.

        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id_user, nom_user, mdp
                          FROM utilisateur
                         ORDER BY id_user;
                        """
                    )
                    rows = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        liste: list[Utilisateur] = []
        if rows:
            dict_like = isinstance(rows[0], dict)
            for r in rows:
                if dict_like:
                    u = Utilisateur(
                        id_user=r["id_user"],
                        nom_user=r["nom_user"],
                        mdp=r["mdp"],
                    )
                else:
                    u = Utilisateur(
                        id_user=r[0],
                        nom_user=r[1],
                        mdp=r[2],
                    )
                liste.append(u)
        return liste

    @log
    def modifier_user(self, utilisateur: Utilisateur) -> bool:
        """
        Modifie les informations d’un utilisateur existant.

        Paramètres
        ----------
        utilisateur : Utilisateur
            Objet contenant :
            - id_user : int (obligatoire)
            - nom_user : str (nouvelle valeur)
            - mdp : str (nouveau mot de passe déjà hashé)

        Retour
        ------
        bool
            - True si exactement une ligne a été modifiée.
            - False sinon.

        Notes
        -----
        - Met à jour les colonnes nom_user et mdp.
        - Ne modifie rien si id_user est invalide.
        - Toute exception SQL est journalisée.
        """
        res = 0
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE utilisateur
                           SET nom_user = %(nom_user)s,
                               mdp      = %(mdp)s
                         WHERE id_user  = %(id_user)s;
                        """,
                        {
                            "nom_user": utilisateur.nom_user,
                            "mdp": utilisateur.mdp,
                            "id_user": utilisateur.id_user,
                        },
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
        return res == 1

    @log
    def supprimer(self, utilisateur: Utilisateur) -> bool:
        """
        Supprime un utilisateur selon son identifiant.

        Paramètres
        ----------
        utilisateur : Utilisateur
            Objet contenant au minimum l’attribut id_user.

        Retour
        ------
        bool
            - True si une ligne a été supprimée.
            - False si aucun utilisateur n’a été trouvé.

        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM utilisateur
                         WHERE id_user = %(id_user)s;
                        """,
                        {"id_user": utilisateur.id_user},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise
        return res > 0

    @log
    def se_connecter(self, nom_user: str, mdp_hash: str) -> Utilisateur | None:
        """
        Authentifie un utilisateur via son nom + mot de passe hashé.

        Paramètres
        ----------
        nom_user : str
            Login fourni par l’utilisateur.
        mdp_hash : str
            Mot de passe hashé, généré côté service.

        Retour
        ------
        Utilisateur | None
            - L’utilisateur authentifié si les identifiants concordent.
            - None sinon ou en cas d’erreur.

        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id_user, nom_user, mdp
                          FROM utilisateur
                         WHERE nom_user = %(nom_user)s
                           AND mdp      = %(mdp)s;
                        """,
                        {"nom_user": nom_user, "mdp": mdp_hash},
                    )
                    row = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            return None

        if not row:
            return None

        return Utilisateur(
            id_user=row["id_user"] if isinstance(row, dict) else row[0],
            nom_user=row["nom_user"] if isinstance(row, dict) else row[1],
            mdp=row["mdp"] if isinstance(row, dict) else row[2],
        )
