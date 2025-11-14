import os
import pytest
from unittest.mock import patch
from datetime import datetime

# Importations nécessaires
from utils.reset_database import ResetDatabase
from dao.log_scan_dao import LogScanDao
from business_object.log_scan import LogScan

#
# SETUP DE TEST (Identique à vos autres tests DAO)
#
@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """
    Initialise une base dédiée aux tests (projet_test_dao)
    et la réinitialise avant chaque test.
    """
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
    yield

#
# TESTS DAO (sur la BDD de test)
#

def test_creer_log_ok():
    """
    Teste l'insertion réussie d'un nouveau log de scan.
    """
    dao = LogScanDao()
    
    # On utilise id_qrcode = 2 (existe dans pop_db_test.sql, mais n'a pas de logs)
    log_scan = LogScan(
        id_qrcode=2,
        client_host="1.1.1.1",
        user_agent="TestAgent-DAO",
        geo_city="TestVille"
    )
    
    # 1. Tenter la création
    success = dao.creer_log(log_scan)
    
    # 2. Vérifier le succès
    assert success is True
    
    # 3. Vérifier que l'objet a été mis à jour avec l'ID de la BDD
    assert log_scan.id_scan is not None
    assert isinstance(log_scan.id_scan, int)
    
    # 4. Vérifier en relisant
    logs_recents = dao.get_scans_recents(id_qrcode=2)
    assert len(logs_recents) == 1
    assert logs_recents[0]['client_host'] == "1.1.1.1"

def test_creer_log_echec_fk():
    """
    Teste que la création échoue (retourne False) si le id_qrcode
    n'existe pas (contrainte de clé étrangère).
    """
    dao = LogScanDao()
    
    log_scan = LogScan(
        id_qrcode=99999, # Cet ID n'existe pas
        client_host="2.2.2.2"
    )
    
    success = dao.creer_log(log_scan)
    
    # Le DAO doit attraper l'exception et retourner False
    assert success is False
    assert log_scan.id_scan is None # L'ID n'a pas été défini

def test_get_scans_recents_ok_avec_data_init():
    """
    Teste la récupération des scans récents pour un QR code
    qui a déjà des logs dans pop_db_test.sql (id_qrcode = 1).
    """
    dao = LogScanDao()
    
    # id_qrcode = 1 a 2 logs dans pop_db_test.sql
    logs = dao.get_scans_recents(id_qrcode=1)
    
    assert isinstance(logs, list)
    assert len(logs) == 2
    
    # Vérifie l'ordre (le plus récent en premier : 14:45:01Z)
    assert logs[0]['client_host'] == '10.0.0.5'
    assert logs[0]['geo_city'] == 'Mountain View'
    assert logs[1]['client_host'] == '192.168.1.10'
    assert logs[1]['geo_city'] == 'Rennes'

def test_get_scans_recents_avec_limit():
    """
    Teste que le paramètre 'limit' est bien respecté.
    """
    dao = LogScanDao()
    
    # id_qrcode = 1 a 2 logs, on en demande 1 seul
    logs = dao.get_scans_recents(id_qrcode=1, limit=1)
    
    assert isinstance(logs, list)
    assert len(logs) == 1
    assert logs[0]['client_host'] == '10.0.0.5' # Le plus récent

def test_get_scans_recents_sans_resultat():
    """
    Teste la récupération pour un QR code existant (id=2)
    mais n'ayant aucun log. Doit retourner [].
    """
    dao = LogScanDao()
    logs = dao.get_scans_recents(id_qrcode=2)
    
    assert isinstance(logs, list)
    assert len(logs) == 0

def test_get_scans_recents_id_inexistant():
    """
    Teste la récupération pour un QR code inexistant (id=999).
    Doit retourner [].
    """
    dao = LogScanDao()
    logs = dao.get_scans_recents(id_qrcode=999)
    
    assert isinstance(logs, list)
    assert len(logs) == 0

if __name__ == "__main__":
    pytest.main([__file__])