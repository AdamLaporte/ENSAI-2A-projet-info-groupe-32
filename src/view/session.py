# src/view/session.py
from datetime import datetime
from utils.singleton import Singleton

class Session(metaclass=Singleton):
    """Session applicative pour l'utilisateur connecté"""

    def __init__(self):
        self.user = None            # objet utilisateur/user connecté
        self.debut_connexion = None   # horodatage lisible
        self.access_token = None  # AJOUT : Token de l'API

    def connexion(self, user, access_token=None): # MODIFIÉ : Ajout de access_token
        """Enregistre l'utilisateur/user en session avec un horodatage et un token API"""
        self.user = user
        self.access_token = access_token # AJOUT
        self.debut_connexion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def deconnexion(self):
        """Purge la session"""
        self.user = None
        self.debut_connexion = None
        self.access_token = None # AJOUT

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
        # AJOUT : Affichage du token (tronqué pour la sécurité)
        token_display = f"{self.access_token[:5]}..." if self.access_token else "Aucun"
        res += f"Token API: {token_display}\n" 
        return res