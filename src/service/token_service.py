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
    def lister_tous(self) -> list[Token]:
        """Lister tous les tokens"""
        return TokenDao().lister_tous()

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

    @log
    def valider_token(self, token_valide) -> bool:
        """Valider si un token est valide (pas expiré)"""
        if not token_valide:
            return False
        return token_valide.expire_dans > datetime.now()

    @log
    def afficher_tous(self) -> str:
        """Afficher tous les tokens sous forme de tableau"""
        entetes = ["utilisateur_id", "token", "expire_dans"]

        tokens = TokenDao().lister_tous()
        tokens_as_list = [t.as_list() for t in tokens]

        str_tokens = "-" * 100
        str_tokens += "\nListe des tokens\n"
        str_tokens += "-" * 100
        str_tokens += "\n"
        str_tokens += tabulate(
            tabular_data=tokens_as_list,
            headers=entetes,
            tablefmt="psql",
            floatfmt=".2f",
        )
        str_tokens += "\n"

        return str_tokens

    @log
    def supprimer_expired_tokens(self) -> int:
        """Supprimer les tokens expirés"""
        tokens_expired = TokenDao().lister_tous_expired()
        for token in tokens_expired:
            TokenDao().supprimer(token)
        return len(tokens_expired)

    @log
    def token_deja_utilise(self, utilisateur_id) -> bool:
        """Vérifie si un utilisateur a déjà un token valide"""
        token = TokenDao().trouver_par_utilisateur_id(utilisateur_id)
        return token is not None and self.valider_token(token)
