class Utilisateur:
    """
    Représente un utilisateur avec id numérique et nom utilisateur textuel.

    Attributs privés
    ----------------
    id_user : int | None
        Identifiant numérique de l'utilisateur.
    nom_user : str | None
        Nom d'utilisateur (login).
    mdp : str | None
        Mot de passe (hashé dans la pratique).
    """

    def __init__(self, id_user=None, nom_user=None, mdp=None):
        if id_user is not None and not isinstance(id_user, int):
            raise ValueError("L'identifiant doit être un entier")
        if nom_user is not None and not isinstance(nom_user, str):
            raise ValueError("Le nom d'utilisateur doit être une chaîne de caractères")
        if mdp is not None and not isinstance(mdp, str):
            raise ValueError("Le mot de passe doit être une chaîne de caractères")

        # --- Attributs privés ---
        self.__id_user = id_user
        self.__nom_user = nom_user
        self.__mdp = mdp

    # ---------------------------------------------------------
    # Getters / Setters utilisant les attributs privés
    # ---------------------------------------------------------

    @property
    def id_user(self):
        return self.__id_user

    @id_user.setter
    def id_user(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("L'identifiant doit être un entier")
        self.__id_user = value

    @property
    def nom_user(self):
        return self.__nom_user

    @nom_user.setter
    def nom_user(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le nom d'utilisateur doit être une chaîne de caractères")
        self.__nom_user = value

    @property
    def mdp(self):
        return self.__mdp

    @mdp.setter
    def mdp(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Le mot de passe doit être une chaîne de caractères")
        self.__mdp = value

    # ---------------------------------------------------------
    # Représentation & comparaison
    # ---------------------------------------------------------

    def __str__(self):
        return f"Utilisateur({self.__id_user}, {self.__nom_user})"

    def __eq__(self, other):
        if not isinstance(other, Utilisateur):
            return False
        # égalité sur la clé si présente, sinon repli sur nom_user
        if self.__id_user is not None and other.__id_user is not None:
            return self.__id_user == other.__id_user
        return self.__nom_user == other.__nom_user
