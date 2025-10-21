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
        Création d'un utilisateur.
        Attend utilisateur.nom_user (str) et utilisateur.mdp (str) remplis.
        Renseigne utilisateur.id_user depuis RETURNING.
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
        """Trouver un utilisateur par id_user (entier)."""
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
        """Trouver un utilisateur par nom_user (login)."""
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
        """Lister tous les utilisateurs."""
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
        Modification d'un utilisateur.
        Met à jour nom_user et/ou mdp selon ce qui est fourni.
        Ici, on met à jour les deux colonnes avec les valeurs présentes.
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
        """Supprimer un utilisateur par id_user."""
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
        Connexion par nom_user + mot de passe hashé (déjà hashé en service).
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
