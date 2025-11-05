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

        self._id_user = id_user
        self._jeton = jeton
        self._date_expiration = date_expiration  

    @property
    def id_user(self):
        return self._id_user

    @id_user.setter
    def id_user(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("L'identifiant 'id_user' doit être un entier.")
        self._id_user = value

    @property
    def jeton(self):
        return self._jeton

    @jeton.setter
    def jeton(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le jeton d'authentification doit être une chaîne de caractères.")
        self._jeton = value

    @property
    def date_expiration(self):
        return self._date_expiration

    @date_expiration.setter
    def date_expiration(self, value):
        if value is not None and not isinstance(value, datetime):
            raise ValueError("La date d'expiration doit être une date.")
        self._date_expiration = value

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self._id_user == other._id_user and self.jeton == other._jeton #ici je ne sais
        #pas si on doit comparer les deux ou que un seul des deux et si oui lequel

    def __repr__(self):
        return f"Token(user_id={self._id_user}, jeton='{self._jeton}',expiration={self._date_expiration})"
