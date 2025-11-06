import pytest
import string
import secrets
from unittest.mock import patch, MagicMock
from datetime import datetime
#from token.db_connection import DBConnection

from business_object.token import Token
from dao.token_dao import TokenDao

#Tests pour generer_jeton

def test_generer_jeton_longueur():
    """Test pour vérifier que la longueur du jeton est correcte."""
    jeton = TokenDao.generer_jeton()
    assert len(jeton) == 32, f"Le jeton doit avoir 32 caractères, mais il a {len(jeton)}."

def test_generer_jeton_chaine():
    """Test pour vérifier que le jeton est une chaîne de caractères."""
    jeton = TokenDao.generer_jeton()
    assert isinstance(jeton, str), "Le jeton doit être une chaîne de caractères."

def test_generer_jeton_unique():
    """Test pour vérifier que deux appels successifs génèrent des jetons différents."""
    jeton1 = TokenDao.generer_jeton()
    jeton2 = TokenDao.generer_jeton()
    assert jeton1 != jeton2, "Deux jetons générés consécutivement ne doivent pas être identiques."

# Tests pour creer_token

def test_creer_token_ok():
    """ Création d'un token réussie avec ID auto-généré. """

    token = Token(id_user=1, jeton="gpVU0x1IzZbP0ScIopiGLlZO5EzhtaAM", date_expiration=datetime(2025, 10, 10, 14, 30))

    ok = TokenDao().creer_token(token)

    assert ok is True  

    # Vérification de l'existence du token dans la base de données
    """ token_db = TokenDao().trouver_par_id_user(token.id_user)
    assert token_db is not None
    assert token_db.id_user == token.id_user
    assert token_db.jeton == token.jeton
    assert token_db.date_expiration == token.date_expiration """

def test_creer_token_echec():
    """Création échouée si données invalides"""
    t = Token(id_user= 10, jeton=None, date_expiration=None)
    ok = TokenDao().creer_token(t)
    assert ok is False

#Test pour trouver_token_par_id

def test_trouver_token_par_id_success():
    """Recherche par id_user d'un utilisateur existant"""
    T = Token(id_user=10, jeton="gpVU0x1IzZbP0ScIopiGLlZO5EzhtaAM", date_expiration = datetime.datetime(2030, 1, 1, 1, 1))
    TokenDao().creer_token(T)

    token  = TokenDao().trouver_token_par_id_user(id_user)
    assert id_user is not None
    assert isinstance(token, Token)
    assert token.jeton == T.jeton
    assert token.date_expiration == T.date_expiration

def test_trouver_token_par_id_echec():
    """Recherche par id_user inexistant"""
    t = TokenDao().trouver_token_par_id(999999)
    assert t is None



