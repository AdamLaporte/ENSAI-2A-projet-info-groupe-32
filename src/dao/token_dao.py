import logging

from utils.singleton import Singleton
from utils.log_decorator import log

from dao.db_connection import DBConnection

from business_object.token import Token
from business_object.utilisateur import Utilisateur


class TokenDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Tokens de la base de données"""

    @log
    def creer_token(self, token: Token): 
        """Création d'un token dans la base de données

        Attributs 
        ----------
        token : Token

        Returns
        -------
        created : bool
            True si la création est un succès
            False sinon
        """
        #difference entre attributs et parameters ?
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO token(id_user, jeton, date_expiration)
                        VALUES (%(id_user)s, %(jeton)s, %(date_expiration)s)
                        RETURNING id_token;
                        """,
                        {
                            "id_user": token.id_user,
                            "jeton": token.jeton,
                            "date_expiration": token.date_expiration,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        created = False
        if res:
            created = True

        return created

    @log
    def trouver_token_par_id(self, Utilisateur, id_user:str): #comment j'importe utilisateur 
        """Trouver un token grâce à son id_user

        Attributs
        ----------
        u.id_user : int
            identifiant du token à trouver

        Returns
        -------
        token : Token
            Renvoie le token correspondant à l'id_user None s'il n'existe pas
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id_user, jeton, date_expiration "
                        "FROM token WHERE id_user = %(id_user)s;",
                        {"id_user": id_user},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        token = None
        if res:
            token = Token(
                jeton=res["jeton"],
                Utilisateur=Utilisateur(id_user=res["id_user"]),
                date_expiration=res["date_expiration"],
            )

        return token

    def supprimer_token(self, token: Token) -> bool:
        """
        Supprime un token de la base de données.

        Attributs
        ----------
        token : Token
            Le token à supprimer

        Returns
        -------
        deleted : bool
            True si la suppression a réussi
            False sinon
        """
        try:
            with DBConnection().connection as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM Token WHERE jeton = %(jeton)s;",
                        {"jeton": Token.jeton}
                    )
                    res = cursor.rowcount  # nombre de lignes affectées
        except Exception as e:
            logging.info(f"Erreur lors de la suppression du token {Token.jeton}: {e}")
            return False

        if res == 1:
            logging.info(f"Token {Token.jeton} supprimé avec succès.")
        else:
            logging.info(f"Aucun token supprimé pour {Token.jeton}.")
        return res == 1

    @log
    def est_valide_token(self, token: Token) -> bool:
        """
        Vérifie si un token est encore valide en termes de date d'expiration.
        Si le token est expiré, il est supprimé de la base de données.

        Attributs
        ----------
        token : Token
            Le token à vérifier

        Returns
        -------
        is_valid : bool
            True si le token est encore valide
            False sinon (et supprime le token expiré)
        """
        try:
            if token.date_expiration is None:
                return False

            now = datetime.now()
            if token.date_expiration < now:
                self.token_dao.supprimer_token(token)
                logging.info(f"Token {Token.jeton} expiré et supprimé de la base")
                return False

            return True
        except Exception as e:
            logging.info(f"Erreur lors de la vérification du token : {e}")
            return False

    @log
    def trouver_id_user_par_token(self, jeton: str) -> str | None:
        """Trouver l'id_user associé à un jeton

        Attribut
        ----------
        jeton : str
            Le jeton à rechercher

        Returns
        -------
        id_user : str
            L'identifiant de l'utilisateur associé au jeton, ou None s'il n'existe pas
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id_user FROM token WHERE jeton = %(jeton)s;",
                        {"jeton": jeton},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            return None

        if res:
            return res["id_user"]
        return None

    @log
    def existe_token(jeton):
         """Vérifie si un token existe dans la base de données

        Attributs 
        ----------
        jeton : str
            Le jeton à vérifier

        Returns
        -------
        bool
            True si le token existe
            False sinon
        """
        try :
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM token WHERE jeton = %(jeton)s LIMIT 1;",
                        {"jeton": jeton},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(f"Erreur lors de la vérification de l'existence du token : {e}")
            return False

        return res is not None
