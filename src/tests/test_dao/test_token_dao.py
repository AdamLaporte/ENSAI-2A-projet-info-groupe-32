import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from dao.token_dao import TokenDao
from business_object.token import Token
from business_object.utilisateur import Utilisateur

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Initialise l'environnement pour TokenDao"""
    with patch.dict("os.environ", {"POSTGRES_SCHEMA": "projet_test_dao"}):
        yield

def test_creer_token_ok():
    """Création de token réussie avec id auto-généré"""
    token = Token(
        id_user=1,
        jeton="xyz123",
        date_expiration=datetime.now() + timedelta(days=1),
    )
    # mocking du cursor/connection
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"id_token": 42}
        ok = TokenDao().creer_token(token)
        assert ok is True

def test_creer_token_ko():
    """Création échouée si données invalides"""
    token = Token(id_user=None, jeton=None, date_expiration=None)
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        ok = TokenDao().creer_token(token)
        assert ok is False

def test_trouver_token_par_id_existant():
    """Recherche par id_user d'un token existant"""
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            "id_user": 17,
            "jeton": "abc99",
            "date_expiration": datetime.now() + timedelta(days=2),
        }
        tok = TokenDao().trouver_token_par_id(Utilisateur, 17)
        assert tok is not None
        assert tok.jeton == "abc99"
        assert isinstance(tok.date_expiration, datetime)

def test_trouver_token_par_id_non_existant():
    """Recherche par id_user inexistant"""
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        tok = TokenDao().trouver_token_par_id(Utilisateur, 999999)
        assert tok is None

def test_supprimer_token_ok():
    """Suppression réussie"""
    token = Token(id_user=10, jeton="toktok", date_expiration=datetime.now())
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        ok = TokenDao().supprimer_token(token)
        assert ok is True

def test_supprimer_token_ko():
    """Suppression échouée si token inexistant"""
    token = Token(id_user=11, jeton="never", date_expiration=datetime.now())
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        ok = TokenDao().supprimer_token(token)
        assert ok is False

def test_est_valide_token_ok():
    """Token valide, non supprimé"""
    token = Token(id_user=22, jeton="valide_one", date_expiration=datetime.now() + timedelta(days=2))
    ok = TokenDao().est_valide_token(token)
    assert ok is True

def test_est_valide_token_ko():
    """Token expiré donc supprimé"""
    token = Token(id_user=23, jeton="expired", date_expiration=datetime.now() - timedelta(days=1))
    with patch.object(TokenDao, "supprimer_token", return_value=True) as patch_sup:
        ok = TokenDao().est_valide_token(token)
        assert ok is False
        patch_sup.assert_called_once_with(token)
    
def test_trouver_id_user_par_token_existant():
    """Recherche id_user par jeton existant"""
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"id_user": 42}
        res = TokenDao().trouver_id_user_par_token("jetonfind")
        assert res == 42

def test_trouver_id_user_par_token_non_existant():
    """Recherche id_user par jeton inexistant"""
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        res = TokenDao().trouver_id_user_par_token("nothing")
        assert res is None

def test_existe_token_ok():
    """Vérifie l'existence réelle d'un jeton"""
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        assert TokenDao().existe_token("real_token") is True

def test_existe_token_ko():
    """Jeton inexistant"""
    with patch("dao.db_connection.DBConnection.connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        assert TokenDao().existe_token("no_token") is False
