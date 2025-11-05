from datetime import datetime
from business_object.utilisateur import Utilisateur as u


class Token:
    """
    Classe représentant un Token

    Attributs
    ----------
    _jeton : str
        jeton d'authentification (privé)
    _id_user : int
        identifiant du joueur lié à ce jeton (privé).
    _date_expiration :
        date d'expiration du jeton (privé)
    """

    def __init__(self, jeton: str, u, date_expiration : datetime ): #comment j'importe u 
        """Constructeur"""
        self._jeton = jeton
        self._id_user = u.id_user
        self._date_expiration = date_expiration

    @property
    def jeton(self):
        return self._jeton

    @jeton.setter
    def jeton(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le jeton d'authentification doit être une chaîne de caractères")
        self._jeton = value

    @property
    def date_expiration(self):
        return self._date_expiration

    @date_expiration.setter
    def date_expiration(self, value):
        if value is not None and not isinstance(value, datetime):
            raise ValueError("La date d'expiration doit être une date")
        self._date_expiration = value

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self._id_user == other._id_user and self.jeton == other._jeton #ici je ne sais
        #pas si on doit comparer les deux ou que un seul des deux et si oui lequel

    def __repr__(self):
        return f"Token(user_id={self._id_user}, jeton='{self._jeton}',expiration={self._date_expiration})"
