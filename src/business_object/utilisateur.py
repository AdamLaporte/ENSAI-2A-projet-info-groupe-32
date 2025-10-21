class Utilisateur:
    """
    Représente un utilisateur avec id numérique et nom utilisateur textuel.
    Attributs:
      _id_user: int | None
      _nom_user: str | None
      _mdp: str | None
    """

    def __init__(self, id_user=None, nom_user=None, mdp=None):
        if id_user is not None and not isinstance(id_user, int):
            raise ValueError("L'identifiant doit être un entier")
        if nom_user is not None and not isinstance(nom_user, str):
            raise ValueError("Le nom d'utilisateur doit être une chaîne de caractères")
        if mdp is not None and not isinstance(mdp, str):
            raise ValueError("Le mot de passe doit être une chaîne de caractères")
        self._id_user = id_user
        self._nom_user = nom_user
        self._mdp = mdp

    @property
    def id_user(self):
        return self._id_user

    @id_user.setter
    def id_user(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("L'identifiant doit être un entier")
        self._id_user = value

    @property
    def nom_user(self):
        return self._nom_user

    @nom_user.setter
    def nom_user(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le nom d'utilisateur doit être une chaîne de caractères")
        self._nom_user = value

    @property
    def mdp(self):
        return self._mdp

    @mdp.setter
    def mdp(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le mot de passe doit être une chaîne de caractères")
        self._mdp = value

    def __str__(self):
        return f"Utilisateur({self._id_user}, {self._nom_user})"

    def __eq__(self, other):
        if not isinstance(other, Utilisateur):
            return False
        # égalité sur la clé si présente, sinon repli sur nom_user
        if self._id_user is not None and other._id_user is not None:
            return self._id_user == other._id_user
        return self._nom_user == other._nom_user
