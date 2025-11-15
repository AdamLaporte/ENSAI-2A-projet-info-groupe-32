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
    Teste la création d’un log de scan.

    Paramètres
    ----------
    Aucun paramètre externe. Les données du log sont construites dans le test.

    Retour
    ------
    None
        Le test valide :
        - que l’insertion retourne True,
        - que l’objet LogScan reçoit un id_scan auto-généré,
        - que la relecture via get_scans_recents confirme l’insertion.

    Notes
    -----
    Le test utilise un id_qrcode existant dans la base de tests (id_qrcode = 2).
    """
    dao = LogScanDao()
    
    log_scan = LogScan(
        id_qrcode=2,
        client_host="1.1.1.1",
        user_agent="TestAgent-DAO",
        geo_city="TestVille"
    )
    
    success = dao.creer_log(log_scan)
    assert success is True
    assert log_scan.id_scan is not None
    assert isinstance(log_scan.id_scan, int)

    logs_recents = dao.get_scans_recents(id_qrcode=2)
    assert len(logs_recents) == 1
    assert logs_recents[0]['client_host'] == "1.1.1.1"


def test_creer_log_echec_fk():
    """
    Teste l’échec de création lorsqu’un id_qrcode invalide est fourni.

    Paramètres
    ----------
    Aucun paramètre externe. Un LogScan est créé avec un id_qrcode inexistant.

    Retour
    ------
    None
        Le test vérifie :
        - que creer_log retourne False,
        - que l’objet LogScan ne reçoit pas d’id_scan.

    Notes
    -----
    Le cas correspond à une violation de clé étrangère,
    que le DAO doit gérer sans lever d’exception.
    """
    dao = LogScanDao()
    
    log_scan = LogScan(
        id_qrcode=99999,
        client_host="2.2.2.2"
    )
    
    success = dao.creer_log(log_scan)
    assert success is False
    assert log_scan.id_scan is None


def test_get_scans_recents_ok_avec_data_init():
    """
    Teste la récupération de logs récents pour un QR code ayant déjà des entrées.

    Paramètres
    ----------
    Aucun paramètre externe. Le test repose sur des données initiales en base
    (id_qrcode = 1).

    Retour
    ------
    None
        Le test confirme :
        - que la liste des logs est correcte,
        - que les logs sont triés du plus récent au plus ancien.

    Notes
    -----
    Les données proviennent du fichier pop_db_test.sql.
    """
    dao = LogScanDao()
    
    logs = dao.get_scans_recents(id_qrcode=1)
    
    assert isinstance(logs, list)
    assert len(logs) == 2
    assert logs[0]['client_host'] == '10.0.0.5'
    assert logs[0]['geo_city'] == 'Mountain View'
    assert logs[1]['client_host'] == '192.168.1.10'
    assert logs[1]['geo_city'] == 'Rennes'


def test_get_scans_recents_avec_limit():
    """
    Teste l’application du paramètre `limit` lors de la récupération des logs.

    Paramètres
    ----------
    Aucun paramètre externe. La fonction est appelée avec limit=1.

    Retour
    ------
    None
        Le test vérifie que :
        - une seule entrée est renvoyée,
        - il s’agit du log le plus récent.

    Notes
    -----
    Le QR code id=1 possède deux logs dans la base de tests.
    """
    dao = LogScanDao()
    
    logs = dao.get_scans_recents(id_qrcode=1, limit=1)
    
    assert isinstance(logs, list)
    assert len(logs) == 1
    assert logs[0]['client_host'] == '10.0.0.5'


def test_get_scans_recents_sans_resultat():
    """
    Teste la récupération des logs pour un QR code existant mais sans historique.

    Paramètres
    ----------
    Aucun paramètre externe. Le test interroge id_qrcode = 2.

    Retour
    ------
    None
        Le test valide que la fonction retourne une liste vide.

    Notes
    -----
    Ce cas correspond à un QR code valide mais jamais scanné.
    """
    dao = LogScanDao()
    logs = dao.get_scans_recents(id_qrcode=2)
    
    assert isinstance(logs, list)
    assert len(logs) == 0


def test_get_scans_recents_id_inexistant():
    """
    Teste la récupération des logs pour un QR code inexistant en base.

    Paramètres
    ----------
    Aucun paramètre externe. Le test interroge id_qrcode = 999.

    Retour
    ------
    None
        Le test vérifie que la fonction renvoie une liste vide.

    Notes
    -----
    Le DAO ne doit pas lever d’exception pour un id_qrcode inconnu.
    """
    dao = LogScanDao()
    logs = dao.get_scans_recents(id_qrcode=999)
    
    assert isinstance(logs, list)
    assert len(logs) == 0


if __name__ == "__main__":
    pytest.main([__file__])