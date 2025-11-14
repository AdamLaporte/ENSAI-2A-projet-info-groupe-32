import pytest
import string
import secrets
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from business_object.token import Token
from dao.token_dao import TokenDao

# Tests pour creer_token

@patch('dao.token_dao.DBConnection')
def test_creer_token_ok(MockDBConnection):
    """ Création d'un token réussie avec ID auto-généré. """

    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.fetchone.return_value = (1,) 

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

## Test pour trouver_token_par_id

@patch('dao.token_dao.DBConnection')
def test_trouver_token_par_id_success(MockDBConnection):
    """ Recherche par id_user d'un utilisateur existant (Mocké) """
    
    id_user_test = 10
    jeton_test = "gpVU0x1IzZbP0ScIopiGLlZO5EzhtaAM"
    date_exp_test = datetime(2030, 1, 1, 1, 1)

    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value

    mock_cursor.fetchone.return_value = {
        "id_user": id_user_test, 
        "jeton": jeton_test, 
        "date_expiration": date_exp_test
    }
    
    token_recupere = TokenDao().trouver_token_par_id(id_user_test)
    
    assert token_recupere is not None
    assert isinstance(token_recupere, Token)
    assert token_recupere.jeton == jeton_test
    assert token_recupere.date_expiration == date_exp_test
    assert token_recupere.id_user == id_user_test 

@patch('dao.token_dao.DBConnection')
def test_trouver_token_par_id_echec(MockDBConnection):
    """ Recherche par id_user inexistant (Mocké) """
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.fetchone.return_value = None 

    token_recupere = TokenDao().trouver_token_par_id(999999) # id inexistant
    assert token_recupere is None


## Tests pour supprimer_token

@patch('dao.token_dao.DBConnection')
def test_supprimer_token_succes(MockDBConnection):
    """Teste la suppression réussie d'un token existant (rowcount == 1)."""
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.rowcount = 1 
    
    token_a_supprimer = Token(id_user=1, jeton="jeton_a_effacer_123", date_expiration=None)
    
    resultat = TokenDao().supprimer_token(token_a_supprimer)
    
    assert resultat is True
    
    mock_cursor.execute.assert_called_once()


@patch('dao.token_dao.DBConnection')
def test_supprimer_token_inexistant(MockDBConnection):
    """Teste la suppression d'un token qui n'existe pas (rowcount == 0)."""
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.rowcount = 0 
    
    token_inexistant = Token(id_user=99, jeton="jeton_inexistant_XYZ", date_expiration=None)
    
    resultat = TokenDao().supprimer_token(token_inexistant)
    
    assert resultat is False


@patch('dao.token_dao.DBConnection')
def test_supprimer_token_erreur_bdd(MockDBConnection):

    """Teste le cas où une exception se produit lors de l'exécution (ex: BDD hors service)."""
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.execute.side_effect = Exception("Erreur de connexion simulée")
    
    token_erreur = Token(id_user=2, jeton="jeton_erreur_BDD", date_expiration=None)
    
    resultat = TokenDao().supprimer_token(token_erreur)
    
    assert resultat is False

## Tests trouver_id_user_par_token

@patch('dao.token_dao.DBConnection')
def test_trouver_id_user_par_token_succes(MockDBConnection):
    """Teste la recherche de l'id_user pour un jeton existant."""
    
    id_user_attendu = "u-456-abc"
    jeton_recherche = "XYZ_TOKEN_123"
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.fetchone.return_value = {"id_user": id_user_attendu} 
    
    resultat_id_user = TokenDao().trouver_id_user_par_token(jeton_recherche)
    
    assert resultat_id_user == id_user_attendu


@patch('dao.token_dao.DBConnection')
def test_trouver_id_user_par_token_echec(MockDBConnection):
    """Teste la recherche de l'id_user pour un jeton inexistant."""
    
    jeton_inexistant = "FAKE_TOKEN_XYZ"
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.fetchone.return_value = None 
    
    resultat_id_user = TokenDao().trouver_id_user_par_token(jeton_inexistant)
    
    assert resultat_id_user is None
    
@patch('dao.token_dao.DBConnection')
def test_trouver_id_user_par_token_erreur_bdd(MockDBConnection):
    """Teste le cas où une erreur se produit lors de l'accès à la BDD."""
    
    # 1. Préparation du mock
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    # Simuler une exception lors de l'exécution
    mock_cursor.execute.side_effect = Exception("Erreur de BDD")
    
    # 2. Exécution
    resultat_id_user = TokenDao().trouver_id_user_par_token("jeton_cause_erreur")
    
    # 3. Assertions
    assert resultat_id_user is None # Le DAO gère l'exception et retourne None

## Tests existe_token

@patch('dao.token_dao.DBConnection')
def test_existe_token_ok(MockDBConnection):
    """Teste l'existence d'un jeton (trouvé)."""
    
    jeton_existant = "EXISTS_TOKEN"
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.fetchone.return_value = {"token": jeton_existant} 
    
    resultat = TokenDao().existe_token(jeton_existant)
    
    assert resultat is True


@patch('dao.token_dao.DBConnection')
def test_existe_token_ko(MockDBConnection):
    """Teste l'existence d'un jeton (non trouvé)."""
    
    jeton_inexistant = "DOES_NOT_EXIST"
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.fetchone.return_value = None 
    
    resultat = TokenDao().existe_token(jeton_inexistant)
    
    assert resultat is False
    
@patch('dao.token_dao.DBConnection')
def test_existe_token_erreur_bdd(MockDBConnection):
    """Teste le cas où une erreur se produit lors de l'accès à la BDD."""
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.execute.side_effect = Exception("Erreur de BDD")
    
    resultat = TokenDao().existe_token("jeton_cause_erreur")
    
    assert resultat is False 