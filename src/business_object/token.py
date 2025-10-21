from datetime import datetime
from src.business_object.utilisateur import Utilisateur as u


class Token:
    """
    Classe représentant un Token

    Attributs
    ----------
    __jeton : str
        jeton d'authentification (privé)
    __id_user : str
        identifiant du joueur lié à ce jeton (privé).
    __date_expiration :
        date d'expiration du jeton (privé)
    """

    def __init__(self, jeton: str, u : Utilisateur, date_expiration : datetime ):
        """Constructeur"""
        self.__jeton = jeton
        self.__id_user = u.id_user
        self.__date_expiration = date_expiration

    @property
    def jeton(self):
        return self.__jeton

    @jeton.setter
    def jeton(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le jeton d'authentification doit être une chaîne de caractères")
        self.__jeton = value

    @property
    def date_expiration(self):
        return self.__date_expiration

    @date_expiration.setter
    def date_expiration(self, value):
        if value is not None and not isinstance(value, datetime):
            raise ValueError("La date d'expiration doit être une date")
        self.__date_expiration = value

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.__id_user == other.__id_user and self.jeton == other.__jeton #ici je ne sais
        #pas si on doit comparer les deux ou que un seul des deux et si oui lequel

    def __repr__(self):
        return f"Token(user_id={self.__id_user}, jeton='{self.__jeton}',expiration={self.__date_expiration})"
