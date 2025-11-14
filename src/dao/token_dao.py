import logging
from datetime import datetime
from utils.singleton import Singleton
from utils.log_decorator import log

from dao.db_connection import DBConnection

from business_object.token import Token
from business_object.utilisateur import Utilisateur

import secrets
import string

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
        
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO token(id_user, jeton, date_expiration)
                        VALUES (%(id_user)s, %(jeton)s, %(date_expiration)s);
                        """,
                        {
                            "id_user": token.id_user,
                            "jeton": token.jeton,
                            "date_expiration": token.date_expiration,
                        },
                    )
                    created = cursor.rowcount == 1                    
                    if created:
                        logging.info(f"Token créé avec succès pour user {token.id_user}")
                    else:
                        logging.error("Échec de la création du token : aucune ligne insérée.")
        except Exception as e:
            created = False
            logging.error(f"Erreur lors de la création du token : {e}")
    
        return created

    @log
    def trouver_token_par_id(self, id_user:str): 

        """Attributs
        ----------
        id_user : int
            Identifiant du token à trouver.

        Returns
        -------
        token : Token
            Renvoie le token correspondant à l'id_user, 
            None s'il n'existe pas
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
                id_user=res["id_user"],
                jeton=res["jeton"],
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
                        {"jeton": token.jeton}
                    )
                    res = cursor.rowcount  # nombre de lignes affectées
        except Exception as e:
            logging.info(f"Erreur lors de la suppression du token {token.jeton}: {e}")
            return False

        if res == 1:
            logging.info(f"Token {token.jeton} supprimé avec succès.")
        else:
            logging.info(f"Aucun token supprimé pour {token.jeton}.")
        return res == 1

    @log
    def trouver_token_par_jeton(self, jeton: str) -> Token | None:
        """Trouver l'objet Token complet associé à un jeton
        ...
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # On sélectionne toutes les colonnes nécessaires pour l'objet Token
                    cursor.execute(
                        "SELECT id_user, jeton, date_expiration "
                        "FROM token WHERE jeton = %(jeton)s;",
                        {"jeton": jeton},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            return None

        if res:
            # On construit l'objet Token complet
            return Token(
                id_user=res["id_user"],
                jeton=res["jeton"],
                date_expiration=res["date_expiration"],
            )
        return None
    @log
    def existe_token(self, jeton: str) -> bool:
        """ Vérifie si un token existe dans la base de données

        Attributs 
        ----------
        self : TokenDao
            L'instance de la classe.
        jeton : str
            Le jeton à vérifier

        Returns
        -------
        bool
            True si le token existe
            False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT token FROM token WHERE jeton = %(jeton)s;",
                        {"jeton": jeton},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(f"Erreur lors de la vérification de l'existence du token : {e}")
            return False

        return res is not None
