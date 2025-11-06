from datetime import datetime


class Token:
    """
    Classe représentant un Token

    Attributs
    ----------
     _id_user : int
        identifiant du joueur lié à ce jeton (privé).
    _jeton : str
        jeton d'authentification (privé)
    _date_expiration :
        date d'expiration du jeton (privé)
    """

    def __init__(self, id_user: int, jeton: str, date_expiration : datetime ):
        """Constructeur"""
        if not isinstance(id_user,int) and id_user is not None  :
            raise ValueError("L'identifiant de l'utilisateur 'id_user' doit être un entier.")
        if not isinstance(jeton, str) and jeton is not None  :
            raise ValueError("Le jeton d'authentification 'jeton' doit être une chaine de caractères.")
        if not isinstance(date_expiration, datetime) and date_expiration is not None :
             raise ValueError("La date d'expiration du jeton 'date_expiration' doit être une date au format datetime.")

        self.__id_user = id_user
        self.__jeton = jeton
        self.__date_expiration = date_expiration  

    @property
    def id_user(self):
        return self.__id_user

    @id_user.setter
    def id_user(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("L'identifiant 'id_user' doit être un entier.")
        self.__id_user = value

    @property
    def jeton(self):
        return self.__jeton

    @jeton.setter
    def jeton(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le jeton d'authentification doit être une chaîne de caractères.")
        self.__jeton = value

    @property
    def date_expiration(self):
        return self.__date_expiration

    @date_expiration.setter
    def date_expiration(self, value):
        if value is not None and not isinstance(value, datetime):
            raise ValueError("La date d'expiration doit être une date.")
        self.__date_expiration = value

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.__id_user == other.__id_user and self.jeton == other.__jeton #ici je ne sais
        #pas si on doit comparer les deux ou que un seul des deux et si oui lequel

    def __repr__(self):
        return f"Token(user_id={self.__id_user}, jeton='{self.__jeton}',expiration={self.__date_expiration})"
