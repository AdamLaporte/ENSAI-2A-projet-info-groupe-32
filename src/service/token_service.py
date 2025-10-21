from utils.log_decorator import log
from dao.token_dao import TokenDao
from business_object.token import Token
from utils.securite import generer_token

import tabulate
import datetime


class TokenService:
    """Classe contenant les méthodes de service pour la gestion des tokens"""

    @log
    def creer(self, utilisateur_id, expire_dans) -> Token:
        """Création d'un nouveau token pour un utilisateur"""
        nouveau_token = Token(
            utilisateur_id=utilisateur_id,
            token=generer_token(),
            expire_dans=expire_dans
        )
        return nouveau_token if TokenDao().creer(nouveau_token) else None


    @log
    def trouver_par_id(self, id_token) -> Token:
        """Trouver un token à partir de l'identifiant de l'utilisateur"""
        return TokenDao().trouver_par_id(id_token)

    @log
    def modifier(self, token) -> Token:
        """Modification d'un token (ex. prolongation de validité)"""
        return token if TokenDao().modifier(token) else None

    @log
    def supprimer(self, token) -> bool:
        """Supprimer un token"""
        return TokenDao().supprimer(token)

    @log
    def trouver_par_utilisateur_id(self, utilisateur_id) -> Token:
        """Trouver un token actif pour un utilisateur donné"""
        return TokenDao().trouver_par_utilisateur_id(utilisateur_id)

    @staticmethod
    @log
    def est_valide_token(token: Token) -> bool:
        """
        Vérifie si un token est encore valide en termes de date d'expiration.

        Parameters
        ----------
        token : Token
            Le token à vérifier

        Returns
        -------
        is_valid : bool
            True si le token est encore valide (date d'expiration future)
            False sinon
        """
        try:
            if token.date_expiration is None:
                return False
            # Comparer la date d'expiration avec la date et heure actuelle
            now = datetime.now().date()  # uniquement la date
            return token.date_expiration >= now
        except Exception as e:
            logging.info(f"Erreur lors de la vérification du token : {e}")
            return False
