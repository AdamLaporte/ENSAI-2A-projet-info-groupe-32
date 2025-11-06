import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from service.token_service import TokenService
from business_object.token import Token

def test_generer_jeton_longueur():
    jeton = TokenService.generer_jeton(16)
    assert isinstance(jeton, str)
    assert len(jeton) == 16

@patch("service.token_service.TokenDao.creer_token")
def test_creer_token_ok(mock_creer_token):
    mock_creer_token.return_value = True
    service = TokenService()
    token = service.creer_token(1)
    assert isinstance(token, Token)
    assert token.id_user == 1
    assert token.date_expiration > datetime.now()

@patch("service.token_service.TokenDao.creer_token")
def test_creer_token_ko(mock_creer_token):
    mock_creer_token.return_value = False
    service = TokenService()
    token = service.creer_token(2)
    assert token is None

@patch("service.token_service.TokenDao.trouver_token_par_id")
def test_trouver_token_par_id(mock_trouver):
    token_attendu = Token(id_user=3, jeton="abc123", date_expiration=datetime.now() + timedelta(hours=1))
    mock_trouver.return_value = token_attendu
    service = TokenService()
    token = service.trouver_token_par_id(3)
    assert token == token_attendu

@patch("service.token_service.TokenDao.supprimer_token")
def test_supprimer_token_ok(mock_supprimer):
    token = Token(id_user=4, jeton="todel", date_expiration=datetime.now())
    mock_supprimer.return_value = True
    service = TokenService()
    assert service.supprimer_token(token) is True

@patch("service.token_service.TokenDao.supprimer_token")
def test_supprimer_token_ko(mock_supprimer):
    token = Token(id_user=5, jeton="notdel", date_expiration=datetime.now())
    mock_supprimer.return_value = False
    service = TokenService()
    assert service.supprimer_token(token) is False

def test_est_valide_token_true():
    token = Token(id_user=6, jeton="valid", date_expiration=datetime.now() + timedelta(days=1))
    assert TokenService.est_valide_token(token) is True

def test_est_valide_token_false():
    token = Token(id_user=7, jeton="expired", date_expiration=datetime.now() - timedelta(days=1))
    assert TokenService.est_valide_token(token) is False

@patch("service.token_service.TokenDao.existe_token")
def test_existe_token_true(mock_existe):
    mock_existe.return_value = True
    assert TokenService.existe_token("jeton1") is True

@patch("service.token_service.TokenDao.existe_token")
def test_existe_token_false(mock_existe):
    mock_existe.return_value = False
    assert TokenService.existe_token("jeton2") is False


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
