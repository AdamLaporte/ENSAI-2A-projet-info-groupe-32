class Utilisateur:
    """
    Classe représentant un Utilisateur

    Attributs
    ----------
    _id_user : str
        identifiant de l'utilisateur (privé)
    _mdp : str
        le mot de passe de l'utilisateur (privé)
    """

    def __init__(self, id_user=None, mdp=None):
        """Constructeur avec validation"""
        if id_user is not None and not isinstance(id_user, str):
            raise ValueError("L'identifiant doit être une chaîne de caractères")
        if mdp is not None and not isinstance(mdp, str):
            raise ValueError("Le mot de passe doit être une chaîne de caractères")

        self._id_user = id_user
        self._mdp = mdp

    @property
    def id_user(self):
        return self._id_user

    @id_user.setter
    def id_user(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("L'identifiant doit être une chaîne de caractères")
        self._id_user = value

    @property
    def mdp(self):
        return self._mdp

    @mdp.setter
    def mdp(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le mot de passe doit être une chaîne de caractères")
        self._mdp = value

    def __str__(self):
        """Permet d'afficher les informations de l'utilisateur"""
        return f"Utilisateur({self._id_user})"

    def __eq__(self, other):
        if not isinstance(other, Utilisateur):
            return False
        return self._id_user == other._id_user
