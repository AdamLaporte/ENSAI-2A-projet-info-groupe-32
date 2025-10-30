# src/view/session.py
from datetime import datetime
from utils.singleton import Singleton

class Session(metaclass=Singleton):
    """Session applicative pour l'utilisateur connecté"""

    def __init__(self):
        self.user = None            # objet utilisateur/user connecté
        self.debut_connexion = None   # horodatage lisible

    def connexion(self, user):
        """Enregistre l'utilisateur/user en session avec un horodatage"""
        self.user = user
        self.debut_connexion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def deconnexion(self):
        """Purge la session"""
        self.user = None
        self.debut_connexion = None

    def afficher(self) -> str:
        """Retourne un résumé lisible de la session"""
        res = "Actuellement en session :\n"
        res += "-------------------------\n"
        # Essaye d'afficher un identifiant parlant si disponible
        nom = None
        if self.user is not None:
            # Priorité aux attributs utilisés dans ton modèle Utilisateur
            # (nom_user dans src/business_object/utilisateur.py),
            # puis alternatives si besoin.
            nom = (
                getattr(self.user, "nom_user", None)
            )
        res += f"utilisateur: {nom if nom else self.user}\n"
        res += f"debut_connexion : {self.debut_connexion}\n"
        return res
