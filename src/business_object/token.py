from src.business_object.utilisateur.py import Utilisateur

class Token:
    """
    Classe représentant un Token

    Attributs
    ----------
    _token : str
        jeton d'authentification (privé)
    _id_user : str
        identifiant du joueur lié à ce jeton (privé).
    """

    def __init__(self, token : str, id_user : str):
        """Constructeur"""
        self._token = token
        self._id_user = id_user

    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le jeton d'authentification doit être une chaîne de caractères")
        self._token = value

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self._id_user == other._id_user