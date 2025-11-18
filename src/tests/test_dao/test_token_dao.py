import os
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

from utils.reset_database import ResetDatabase
from dao.token_dao import TokenDao
from business_object.token import Token


#
# SETUP DE TEST (Utilise la VRAIE BDD de test)
#
@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """
    Initialise une base dédiée aux tests.
    Scope="function" : la base est réinitialisée AVANT CHAQUE TEST.
    """
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
    yield


#
# TESTS DAO (corrigés, sans mocks)
#


def test_creer_token_ok():
    """Création d'un token réussie."""
    dao = TokenDao()

    user_id = 3
    token = Token(
        id_user=user_id,
        jeton="un_jeton_de_test_valide_123",
        date_expiration=datetime.now(timezone.utc) + timedelta(days=1),
    )

    ok = dao.creer_token(token)
    assert ok is True

    token_db = dao.trouver_token_par_id(user_id)
    assert token_db is not None
    assert token_db.id_user == token.id_user
    assert token_db.jeton == token.jeton


def test_creer_token_echec_user_inexistant():
    """Création échouée si l'id_user n'existe pas (contrainte de clé étrangère)."""
    dao = TokenDao()
    token = Token(
        id_user=99999,
        jeton="jeton_pour_user_fantome",
        date_expiration=datetime.now(timezone.utc) + timedelta(days=1),
    )

    ok = dao.creer_token(token)
    assert ok is False


def test_trouver_token_par_id_success():
    """
    Recherche par id_user d'un token existant.
    'test_u1' (id 1) a un token dans pop_db_test.sql.

    """
    dao = TokenDao()
    id_user_test = 1

    token_recupere = dao.trouver_token_par_id(id_user_test)

    assert token_recupere is not None
    assert isinstance(token_recupere, Token)
    assert token_recupere.jeton == "tok_test_u1"
    assert token_recupere.id_user == id_user_test


def test_trouver_token_par_id_echec():
    """
    Recherche par id_user d'un utilisateur sans token.
    'test_u3' (id 3) n'a pas de token dans pop_db_test.sql.

    """
    dao = TokenDao()
    id_user_test = 3

    token_recupere = dao.trouver_token_par_id(id_user_test)
    assert token_recupere is None


def test_trouver_token_par_jeton_success():
    """
    Teste la VRAIE méthode : trouver_token_par_jeton (succès).
    """
    dao = TokenDao()
    jeton_test = "tok_test_u1"

    token_recupere = dao.trouver_token_par_jeton(jeton_test)

    assert token_recupere is not None
    assert isinstance(token_recupere, Token)
    assert token_recupere.id_user == 1
    assert token_recupere.jeton == jeton_test


def test_trouver_token_par_jeton_echec():
    """
    Teste la VRAIE méthode : trouver_token_par_jeton (échec).
    """
    dao = TokenDao()
    jeton_test = "jeton_inexistant_XYZ"

    token_recupere = dao.trouver_token_par_jeton(jeton_test)
    assert token_recupere is None


def test_supprimer_token_succes():
    """Teste la suppression réussie d'un token."""
    dao = TokenDao()
    id_user_test = 1
    jeton_test = "tok_test_u1"

    token_a_supprimer = dao.trouver_token_par_id(id_user_test)
    assert token_a_supprimer is not None
    assert token_a_supprimer.jeton == jeton_test

    resultat = dao.supprimer_token(token_a_supprimer)
    assert resultat is True

    token_supprime = dao.trouver_token_par_id(id_user_test)
    assert token_supprime is None


def test_existe_token_ok():
    """Teste l'existence d'un jeton (trouvé)."""
    dao = TokenDao()
    jeton_existant = "tok_test_u2"
    resultat = dao.existe_token(jeton_existant)
    assert resultat is True


def test_existe_token_ko():
    """Teste l'existence d'un jeton (non trouvé)."""
    dao = TokenDao()
    jeton_inexistant = "jeton_inexistant_XYZ"
    resultat = dao.existe_token(jeton_inexistant)
    assert resultat is False


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
