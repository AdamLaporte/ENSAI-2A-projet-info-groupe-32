import pytest
from unittest.mock import patch, MagicMock, ANY

# Importations nécessaires
from service.log_scan_service import LogScanService
from business_object.log_scan import LogScan
# On importe le DAO juste pour pouvoir le mocker
from dao.log_scan_dao import LogScanDao 

#
# TESTS UNITAIRES (avec Mocks)
#

# On prépare un mock de l'instance DAO
mock_dao_instance = MagicMock(spec=LogScanDao)

@patch('service.log_scan_service.LogScanDao', return_value=mock_dao_instance)
def test_enregistrer_log_ok(mock_dao_class):
    """
    Teste que le service crée un objet LogScan
    et appelle le DAO avec.
    """
    # Réinitialiser le mock avant le test
    mock_dao_instance.reset_mock()
    
    # Le DAO simulé retourne True (succès)
    mock_dao_instance.creer_log.return_value = True
    
    # CORRECTION : Injecter le mock manuellement pour être sûr
    service = LogScanService(dao=mock_dao_instance)
    
    params = {
        "id_qrcode": 1,
        "client_host": "3.3.3.3",
        "user_agent": "TestAgent-Service",
        "referer": "http://google.com",
        "accept_language": "en-US",
        "geo_country": "USA",
        "geo_region": "CA",
        "geo_city": "LA"
    }
    
    # 1. Appeler le service
    log_cree = service.enregistrer_log(**params)
    
    # 2. Vérifier le résultat
    # Le service doit retourner l'objet LogScan créé
    assert log_cree is not None
    assert isinstance(log_cree, LogScan)
    assert log_cree.client_host == "3.3.3.3"
    assert log_cree.geo_city == "LA"
    
    # 3. Vérifier que le DAO a été appelé correctement
    # On vérifie qu'il a été appelé 1 fois avec l'objet qu'on a reçu
    mock_dao_instance.creer_log.assert_called_once_with(log_cree)

@patch('service.log_scan_service.LogScanDao', return_value=mock_dao_instance)
def test_enregistrer_log_echec_dao(mock_dao_class):
    """
    Teste le cas où le DAO échoue (retourne False).
    Le service doit alors retourner None.
    """
    mock_dao_instance.reset_mock()
    
    # Le DAO simulé retourne False (échec)
    mock_dao_instance.creer_log.return_value = False
    
    # CORRECTION : Injecter le mock manuellement
    service = LogScanService(dao=mock_dao_instance)
    
    # 1. Appeler le service
    log_cree = service.enregistrer_log(id_qrcode=2, client_host="4.4.4.4")
    
    # 2. Vérifier le résultat
    # Le service doit retourner None
    assert log_cree is None
    
    # 3. Vérifier que le DAO a bien été appelé
    # (ANY = n'importe quel objet, car l'objet créé n'est pas retourné)
    mock_dao_instance.creer_log.assert_called_once_with(ANY)
    # Vérifions que l'argument était bien un LogScan
    args, _ = mock_dao_instance.creer_log.call_args
    assert isinstance(args[0], LogScan)

@patch('service.log_scan_service.LogScanDao', return_value=mock_dao_instance)
def test_enregistrer_log_exception_service(mock_dao_class):
    """
    Teste le cas où une exception (ex: BDD) survient dans le DAO
    et que le service la gère (try...except) en retournant None.
    """
    mock_dao_instance.reset_mock()
    
    # Le DAO simulé lève une exception
    mock_dao_instance.creer_log.side_effect = Exception("Erreur BDD simulée")
    
    # CORRECTION : Injecter le mock manuellement
    service = LogScanService(dao=mock_dao_instance)
    
    # 1. Appeler le service
    log_cree = service.enregistrer_log(id_qrcode=3, client_host="5.5.5.5")
    
    # 2. Vérifier le résultat
    # Le service doit attraper l'exception et retourner None
    assert log_cree is None
    
    # 3. Vérifier que le DAO a bien été appelé
    mock_dao_instance.creer_log.assert_called_once_with(ANY)

if __name__ == "__main__":
    pytest.main([__file__])