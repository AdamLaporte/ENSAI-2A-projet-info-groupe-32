class Token:
    """
    Classe représentant un Token

    Attributs
    ----------
    token : str
        jeton d'authentification
    id_user : str
        identifiant du joueur lié à ce jeton.
    """
    def __init__(self, token : str, id_user : str) :
        """Constructeur"""
        self.token = token
        self.id_user = id_user

    def __str__(self):
        """Permet d'afficher les informations du Token"""
        return f"Token({self.token}, {self.id_user})"