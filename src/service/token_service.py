from utils.log_decorator import log
from dao.token_dao import TokenDao
from business_object.token import Token
from utils.securite import generer_token

import tabulate
import datetime

import secrets
import string


class TokenService:
    """Classe contenant les méthodes de service pour la gestion des tokens"""
    
    def generer_jeton(longueur=32):
         """ Génère un jeton d'authentification sécurisé.
    
    Attributs:
    ----------
        longueur :int
            Longueur du jeton (par défaut 32 caractères)
    
    Returns:
    --------
        str
            Jeton d'authentification aléatoire
    """
    # Utilise secrets pour une génération cryptographiquement sécurisée
    caracteres = string.ascii_letters + string.digits
    jeton = ''.join(secrets.choice(caracteres) for _ in range(longueur))
    return jeton


    @log
    def creer_token(self, id_user) -> Token:
        """Création d'un nouveau token pour un utilisateur
        
        Attributs
        ---------
        id_user : int
            identifiant de l'utilisateur  
        
        Return
        ------

        """
        nouveau_token = Token(
            id_user=id_user,
            jeton=generer_jeton(),
            date_expiration = datetime.now() + timedelta(hours=1) #le jeton est valide une heure 
        )
        return nouveau_token if TokenDao().creer_token(nouveau_token) else None

    @log
    def existe_token(self, id_user):
        pass
    @log
    def trouver_token_par_id(self, id_user) -> Token:
        """Trouver un token à partir de l'identifiant de l'utilisateur
        
        Attributs
        ---------
        id_user : int
            identifiant de l'utilisateur  

        Return
        ------
        token : Token
            Renvoie le token correspondant à l'id_user None s'il n'existe pas
        """
        return TokenDao().trouver_token_par_id(id_user)


    @log
    def supprimer_token(self, token) -> bool:
        """Supprimer un token
        
         Attributs
        ----------
        token : Token
            Le token à supprimer

        Returns
        -------
        deleted : bool
            True si la suppression a réussi
            False sinon"""
        return TokenDao().supprimer_token(token)


    @staticmethod
    @log
    def est_valide_token(token: Token) -> bool:
        """
        Vérifie si un token est encore valide en termes de date d'expiration.

        Attributs
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

    @log
    def existe_token():
        pass

