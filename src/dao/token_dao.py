import logging

from utils.singleton import Singleton
from utils.log_decorator import log

from dao.db_connection import DBConnection

from business_object.token import Token


class TokenDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Tokens de la base de données"""

    @log
    def creer_token(self, token) -> bool:
        """Création d'un token dans la base de données

        Parameters
        ----------
        token : Token

        Returns
        -------
        created : bool
            True si la création est un succès
            False sinon
        """

        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO token(utilisateur.id_user, jeton, date_expiration) VALUES"
                        "(%(id_user)s, %(token)s, %(expire_dans)s) "
                        "RETURNING id_token;",
                        {
                            "utilisateur_id": token.utilisateur_id,
                            "token": token.token,
                            "expire_dans": token.expire_dans,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        created = False
        if res:
            token.id_token = res["id_token"]
            created = True

        return created

    @log
    def trouver_par_id(self, id_token) -> Token:
        """Trouver un token grâce à son id

        Parameters
        ----------
        id_token : int
            ID du token à retrouver

        Returns
        -------
        token : Token
            Renvoie le token correspondant à l'id
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * "
                        "FROM token "
                        "WHERE id_token = %(id_token)s;",
                        {"id_token": id_token},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        token = None
        if res:
            token = Token(
                id_token=res["id_token"],
                utilisateur_id=res["utilisateur_id"],
                token=res["token"],
                expire_dans=res["expire_dans"],
            )

        return token

    @log
    def lister_tous(self) -> list[Token]:
        """Lister tous les tokens

        Parameters
        ----------
        None

        Returns
        -------
        liste_tokens : list[Token]
            Renvoie la liste de tous les tokens de la base de données
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * "
                        "FROM token;"
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        liste_tokens = []

        if res:
            for row in res:
                token = Token(
                    id_token=row["id_token"],
                    utilisateur_id=row["utilisateur_id"],
                    token=row["token"],
                    expire_dans=row["expire_dans"],
                )
                liste_tokens.append(token)

        return liste_tokens

    @log
    def modifier(self, token) -> bool:
        """Modification d'un token dans la base de données

        Parameters
        ----------
        token : Token

        Returns
        -------
        modified : bool
            True si la modification est un succès
            False sinon
        """

        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE token "
                        "SET utilisateur_id = %(utilisateur_id)s, "
                        "    token = %(token)s, "
                        "    expire_dans = %(expire_dans)s "
                        "WHERE id_token = %(id_token)s;",
                        {
                            "utilisateur_id": token.utilisateur_id,
                            "token": token.token,
                            "expire_dans": token.expire_dans,
                            "id_token": token.id_token,
                        },
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)

        return res == 1

    @log
    def supprimer(self, token) -> bool:
        """Suppression d'un token dans la base de données

        Parameters
        ----------
        token : Token

        Returns
        -------
        deleted : bool
            True si la suppression est un succès
            False sinon
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM token "
                        "WHERE id_token = %(id_token)s;",
                        {"id_token": token.id_token},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise

        return res > 0

    @log
    def trouver_par_utilisateur_id(self, utilisateur_id) -> Token:
        """Trouver un token actif pour un utilisateur donné

        Parameters
        ----------
        utilisateur_id : int
            ID de l'utilisateur pour lequel on cherche un token

        Returns
        -------
        token : Token
            Renvoie le token actif de l'utilisateur
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * "
                        "FROM token "
                        "WHERE utilisateur_id = %(utilisateur_id)s "
                        "AND expire_dans > NOW();",
                        {"utilisateur_id": utilisateur_id},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        token = None
        if res:
            token = Token(
                id_token=res["id_token"],
                utilisateur_id=res["utilisateur_id"],
                token=res["token"],
                expire_dans=res["expire_dans"],
            )

        return token

    @log
    def supprimer_expired_tokens(self) -> int:
        """Supprimer les tokens expirés

        Parameters
        ----------
        None

        Returns
        -------
        deleted_count : int
            Nombre de tokens supprimés
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM token "
                        "WHERE expire_dans < NOW();"
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise

        return res
