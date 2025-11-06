import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from service.token_service import TokenService
from business_object.token import Token
# TokenDao n'a pas besoin d'être importé car il est mocké ?


## Tests pour generer_jeton 

def test_generer_jeton_longueur():
    """Teste la génération de jeton avec différentes longueurs."""
    jeton_defaut = TokenService.generer_jeton()
    assert isinstance(jeton_defaut, str)
    assert len(jeton_defaut) == 32

    jeton_specifique = TokenService.generer_jeton(16)
    assert isinstance(jeton_specifique, str)
    assert len(jeton_specifique) == 16


## Tests pour creer_token

@patch("service.token_service.TokenDao.creer_token")
@patch("service.token_service.TokenService.generer_jeton") 
@patch("service.token_service.datetime") 
def test_creer_token_ok(mock_datetime, mock_generer_jeton, mock_creer_token):
    """Teste la création réussie d'un token (retourne un objet Token)."""
    
    mock_generer_jeton.return_value = "SIMULATED_JETON_1"
    mock_creer_token.return_value = True
    
    temps_fixe = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.now.return_value = temps_fixe
    mock_datetime.timedelta = timedelta
    
    service = TokenService()
    id_user_test = 1
    token = service.creer_token(id_user_test)
    
    assert isinstance(token, Token)
    assert token.id_user == id_user_test
    assert token.jeton == "SIMULATED_JETON_1"
    assert token.date_expiration == datetime(2025, 1, 1, 11, 0, 0)
    
    mock_creer_token.assert_called_once()
    assert mock_creer_token.call_args[0][0].jeton == "SIMULATED_JETON_1"


@patch("service.token_service.TokenDao.creer_token")
@patch("service.token_service.TokenService.generer_jeton") 
@patch("service.token_service.datetime")
def test_creer_token_ko(mock_datetime, mock_generer_jeton, mock_creer_token):
    """Teste l'échec de la création du token par le DAO (retourne None)."""
    
    mock_generer_jeton.return_value = "SIMULATED_JETON_2"
    mock_creer_token.return_value = False 
    mock_datetime.now.return_value = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.timedelta = timedelta

    service = TokenService()
    token = service.creer_token(2)
    
    assert token is None
    mock_creer_token.assert_called_once()


## Tests pour trouver_token_par_id

@patch("service.token_service.TokenDao.trouver_token_par_id")
def test_trouver_token_par_id_ok(mock_trouver):
    """Teste la recherche réussie d'un token par ID utilisateur."""
    id_user_test = 3
    token_attendu = Token(id_user=id_user_test, jeton="abc123", date_expiration=datetime.now() + timedelta(hours=1))
    mock_trouver.return_value = token_attendu
    
    service = TokenService()
    token = service.trouver_token_par_id(id_user_test)
    
    assert token == token_attendu
    mock_trouver.assert_called_once_with(id_user_test)

@patch("service.token_service.TokenDao.trouver_token_par_id")
def test_trouver_token_par_id_ko(mock_trouver):
    """Teste la recherche d'un token qui n'existe pas."""
    mock_trouver.return_value = None
    
    service = TokenService()
    token = service.trouver_token_par_id(999)
    
    assert token is None


## Tests pour supprimer_token

@patch("service.token_service.TokenDao.supprimer_token")
def test_supprimer_token_ok(mock_supprimer):
    """Teste la suppression réussie de token."""
    token = Token(id_user=4, jeton="todel", date_expiration=datetime.now())
    mock_supprimer.return_value = True
    
    service = TokenService()
    assert service.supprimer_token(token) is True
    mock_supprimer.assert_called_once_with(token)

@patch("service.token_service.TokenDao.supprimer_token")
def test_supprimer_token_ko(mock_supprimer):
    """Teste l'échec de la suppression de token."""
    token = Token(id_user=5, jeton="notdel", date_expiration=datetime.now())
    mock_supprimer.return_value = False
    
    service = TokenService()
    assert service.supprimer_token(token) is False
    mock_supprimer.assert_called_once_with(token)


## Tests pour est_valide_token (Méthode Statique)

@patch("service.token_service.datetime")
def test_est_valide_token_valide(mock_datetime):
    """Teste un token non expiré (comparaison date et heure)."""
    
    temps_actuel = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.now.return_value = temps_actuel
    
    token = Token(id_user=6, jeton="valid", date_expiration=temps_actuel + timedelta(seconds=1))
    
    assert TokenService.est_valide_token(token) is True

@patch("service.token_service.datetime")
def test_est_valide_token_expire(mock_datetime):
    """Teste un token expiré (comparaison date et heure)."""
    
    temps_actuel = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.now.return_value = temps_actuel
    
    token = Token(id_user=7, jeton="expired", date_expiration=temps_actuel - timedelta(seconds=1))
    
    assert TokenService.est_valide_token(token) is False

def test_est_valide_token_sans_date():
    """Teste le cas où la date d'expiration est None."""
    token = Token(id_user=8, jeton="nodate", date_expiration=None)
    assert TokenService.est_valide_token(token) is False


## Tests pour existe_token

@patch("service.token_service.TokenDao.existe_token")
def test_existe_token_true(mock_existe):
    """Teste l'existence d'un token (DAO retourne True)."""
    jeton_test = "jeton1"
    mock_existe.return_value = True
    
    service = TokenService()
    assert service.existe_token(jeton_test) is True
    mock_existe.assert_called_once_with(jeton_test)

@patch("service.token_service.TokenDao.existe_token")
def test_existe_token_false(mock_existe):
    """Teste l'existence d'un token (DAO retourne False)."""
    jeton_test = "jeton2"
    mock_existe.return_value = False
    
    service = TokenService()
    assert service.existe_token(jeton_test) is False
    mock_existe.assert_called_once_with(jeton_test)