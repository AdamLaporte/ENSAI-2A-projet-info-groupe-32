import pytest
import string
import secrets
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
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

@patch('dao.token_dao.DBConnection')
def test_creer_token_ok(MockDBConnection):
    """ Création d'un token réussie avec ID auto-généré. """

    # Configurer le mock pour simuler une connexion et un curseur qui réussit
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    # Simuler le RETURNING id_token (par exemple, retourner l'ID 1)
    mock_cursor.fetchone.return_value = (1,) 

    token = Token(id_user=1, jeton="gpVU0x1IzZbP0ScIopiGLlZO5EzhtaAM", date_expiration=datetime(2025, 10, 10, 14, 30))

    # L'appel à creer_token va maintenant utiliser la DBConnection mockée
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

# Test pour trouver_token_par_id

@patch('dao.token_dao.DBConnection')
def test_trouver_token_par_id_success(MockDBConnection):
    """ Recherche par id_user d'un utilisateur existant (Mocké) """
    
    id_user_test = 10
    jeton_test = "gpVU0x1IzZbP0ScIopiGLlZO5EzhtaAM"
    date_exp_test = datetime(2030, 1, 1, 1, 1)

    # Configurer le mock pour simuler la connexion et le curseur
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
    assert token_recupere.id_user == id_user_test # Vérifier l'objet Utilisateur

@patch('dao.token_dao.DBConnection')
def test_trouver_token_par_id_echec(MockDBConnection):
    """ Recherche par id_user inexistant (Mocké) """
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    mock_cursor.fetchone.return_value = None 

    token_recupere = TokenDao().trouver_token_par_id(999999) # id inexistant
    assert token_recupere is None


# Tests pour supprimer_token

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



# ====================================================================
# TESTS POUR est_valide_token
# ====================================================================

# Mocke la classe datetime pour contrôler 'now' et la méthode de suppression pour l'isolation
@patch('dao.token_dao.datetime') 
@patch.object(TokenDao, 'supprimer_token') 
def test_est_valide_token_valide(mock_supprimer_token, mock_datetime):
    """Teste un token qui n'a pas expiré."""
    
    # 1. Configuration du temps actuel et d'expiration
    now = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.now.return_value = now
    
    # Expiration future (valide)
    token_valide = Token(id_user=1, jeton="valid", date_expiration=now + timedelta(hours=1))
    
    # 2. Exécution
    resultat = TokenDao().est_valide_token(token_valide)
    
    # 3. Assertions
    assert resultat is True
    # Vérifie que la suppression N'A PAS été appelée
    mock_supprimer_token.assert_not_called()

@patch('dao.token_dao.datetime')
@patch.object(TokenDao, 'supprimer_token')
def test_est_valide_token_expire(mock_supprimer_token, mock_datetime):
    """Teste un token expiré. Il devrait être invalide ET supprimé."""
    
    # 1. Configuration du temps actuel et d'expiration
    now = datetime(2025, 1, 1, 10, 0, 0)
    mock_datetime.now.return_value = now
    
    # Expiration passée (expiré)
    token_expire = Token(id_user=1, jeton="expired", date_expiration=now - timedelta(seconds=1))
    
    # 2. Exécution
    resultat = TokenDao().est_valide_token(token_expire)
    
    # 3. Assertions
    assert resultat is False
    # Vérifie que la suppression A été appelée avec l'objet Token
    mock_supprimer_token.assert_called_once_with(token_expire)

def test_est_valide_token_sans_date_expiration():
    """Teste un token sans date d'expiration (None). Il devrait être invalide."""
    
    token_sans_date = Token(id_user=1, jeton="nodate", date_expiration=None)
    
    # 2. Exécution
    resultat = TokenDao().est_valide_token(token_sans_date)
    
    # 3. Assertions
    assert resultat is False

# ====================================================================
# TESTS POUR trouver_id_user_par_token
# ====================================================================

@patch('dao.token_dao.DBConnection')
def test_trouver_id_user_par_token_succes(MockDBConnection):
    """Teste la recherche de l'id_user pour un jeton existant."""
    
    # 1. Préparation du mock
    id_user_attendu = "u-456-abc"
    jeton_recherche = "XYZ_TOKEN_123"
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    # Simuler le résultat de la BDD (retourne l'id_user)
    mock_cursor.fetchone.return_value = {"id_user": id_user_attendu} 
    
    # 2. Exécution
    resultat_id_user = TokenDao().trouver_id_user_par_token(jeton_recherche)
    
    # 3. Assertions
    assert resultat_id_user == id_user_attendu


@patch('dao.token_dao.DBConnection')
def test_trouver_id_user_par_token_echec(MockDBConnection):
    """Teste la recherche de l'id_user pour un jeton inexistant."""
    
    # 1. Préparation du mock
    jeton_inexistant = "FAKE_TOKEN_XYZ"
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    # Simuler le résultat de la BDD (ne trouve rien)
    mock_cursor.fetchone.return_value = None 
    
    # 2. Exécution
    resultat_id_user = TokenDao().trouver_id_user_par_token(jeton_inexistant)
    
    # 3. Assertions
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

# ====================================================================
# TESTS POUR existe_token
# ====================================================================

@patch('dao.token_dao.DBConnection')
def test_existe_token_oui(MockDBConnection):
    """Teste l'existence d'un jeton (trouvé)."""
    
    # 1. Préparation du mock
    jeton_existant = "EXISTS_TOKEN"
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    # Simuler le résultat de la BDD (trouve quelque chose)
    # Note : La colonne sélectionnée est 'token' dans le DAO
    mock_cursor.fetchone.return_value = {"token": jeton_existant} 
    
    # 2. Exécution (Appel sur la CLASSE car la méthode n'a pas 'self' dans le DAO)
    resultat = TokenDao.existe_token(jeton_existant)
    
    # 3. Assertions
    assert resultat is True


@patch('dao.token_dao.DBConnection')
def test_existe_token_non(MockDBConnection):
    """Teste l'existence d'un jeton (non trouvé)."""
    
    # 1. Préparation du mock
    jeton_inexistant = "DOES_NOT_EXIST"
    
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    # Simuler le résultat de la BDD (ne trouve rien)
    mock_cursor.fetchone.return_value = None 
    
    # 2. Exécution
    resultat = TokenDao.existe_token(jeton_inexistant)
    
    # 3. Assertions
    assert resultat is False
    
@patch('dao.token_dao.DBConnection')
def test_existe_token_erreur_bdd(MockDBConnection):
    """Teste le cas où une erreur se produit lors de l'accès à la BDD."""
    
    # 1. Préparation du mock
    mock_conn = MockDBConnection.return_value.connection.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    # Simuler une exception lors de l'exécution
    mock_cursor.execute.side_effect = Exception("Erreur de BDD")
    
    # 2. Exécution
    resultat = TokenDao.existe_token("jeton_cause_erreur")
    
    # 3. Assertions
    assert resultat is False # Le DAO gère l'exception et retourne False