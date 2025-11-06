import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from service.token_service import TokenService
from business_object.token import Token
# Note: TokenDao n'a pas besoin d'être importé ici, car il est mocké.


## 1. Tests pour generer_jeton (Méthode Statique/Classe)
# ---------------------------------------------------------------------------------

def test_generer_jeton_longueur():
    """Teste la génération de jeton avec différentes longueurs."""
    # Test avec la longueur par défaut (32)
    jeton_defaut = TokenService.generer_jeton()
    assert isinstance(jeton_defaut, str)
    assert len(jeton_defaut) == 32
    
    # Test avec une longueur spécifique (16)
    jeton_specifique = TokenService.generer_jeton(16)
    assert isinstance(jeton_specifique, str)
    assert len(jeton_specifique) == 16


## 2. Tests pour creer_token
# ---------------------------------------------------------------------------------

# Mock du DAO pour l'insertion et de TokenService.generer_jeton pour la stabilité
@patch("service.token_service.TokenDao.creer_token")
@patch("service.token_service.TokenService.generer_jeton") 
@patch("service.token_service.datetime") # Mock de datetime pour contrôler l'heure de création
def test_creer_token_ok(mock_datetime, mock_generer_jeton, mock_creer_token):
    """Teste la création réussie d'un token (retourne un objet Token)."""
    
    # Configuration des mocks
    mock_generer_jeton.return_value = "SIMULATED_JETON_1"
    mock_creer_token.return_value = True
    
    # Contrôler le temps pour vérifier la date d'expiration (+1 heure)
    temps_fixe = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.now.return_value = temps_fixe
    mock_datetime.timedelta = timedelta # S'assurer que timedelta est disponible
    
    service = TokenService()
    id_user_test = 1
    token = service.creer_token(id_user_test)
    
    # Assertions
    assert isinstance(token, Token)
    assert token.id_user == id_user_test
    assert token.jeton == "SIMULATED_JETON_1"
    # Vérification de l'expiration: temps_fixe + 1 heure
    assert token.date_expiration == datetime(2025, 1, 1, 11, 0, 0)
    
    # Vérifier que le DAO a été appelé correctement
    mock_creer_token.assert_called_once()
    assert mock_creer_token.call_args[0][0].jeton == "SIMULATED_JETON_1"


@patch("service.token_service.TokenDao.creer_token")
@patch("service.token_service.TokenService.generer_jeton") 
@patch("service.token_service.datetime")
def test_creer_token_ko(mock_datetime, mock_generer_jeton, mock_creer_token):
    """Teste l'échec de la création du token par le DAO (retourne None)."""
    
    # Configuration des mocks
    mock_generer_jeton.return_value = "SIMULATED_JETON_2"
    mock_creer_token.return_value = False # Simulation de l'échec du DAO
    mock_datetime.now.return_value = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.timedelta = timedelta

    service = TokenService()
    token = service.creer_token(2)
    
    # Assertion
    assert token is None
    mock_creer_token.assert_called_once()


## 3. Tests pour trouver_token_par_id
# ---------------------------------------------------------------------------------

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


## 4. Tests pour supprimer_token
# ---------------------------------------------------------------------------------

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


## 5. Tests pour est_valide_token (Méthode Statique)
# ---------------------------------------------------------------------------------

# Nous mockons datetime pour garantir que la comparaison est stable
@patch("service.token_service.datetime")
def test_est_valide_token_valide(mock_datetime):
    """Teste un token non expiré (comparaison date et heure)."""
    
    # now = 2025-01-01 10:00:00
    temps_actuel = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.now.return_value = temps_actuel
    
    # Expiration = 2025-01-01 10:00:01 (Futur)
    token = Token(id_user=6, jeton="valid", date_expiration=temps_actuel + timedelta(seconds=1))
    
    # Appel sur la classe (méthode statique)
    assert TokenService.est_valide_token(token) is True

@patch("service.token_service.datetime")
def test_est_valide_token_expire(mock_datetime):
    """Teste un token expiré (comparaison date et heure)."""
    
    # now = 2025-01-01 10:00:00
    temps_actuel = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.now.return_value = temps_actuel
    
    # Expiration = 2025-01-01 09:59:59 (Passé)
    token = Token(id_user=7, jeton="expired", date_expiration=temps_actuel - timedelta(seconds=1))
    
    assert TokenService.est_valide_token(token) is False

def test_est_valide_token_sans_date():
    """Teste le cas où la date d'expiration est None."""
    token = Token(id_user=8, jeton="nodate", date_expiration=None)
    assert TokenService.est_valide_token(token) is False


## 6. Tests pour existe_token
# ---------------------------------------------------------------------------------

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