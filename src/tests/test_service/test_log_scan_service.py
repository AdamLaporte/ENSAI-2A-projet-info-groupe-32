import pytest
from unittest.mock import patch, MagicMock, ANY
from service.log_scan_service import LogScanService
from business_object.log_scan import LogScan
from dao.log_scan_dao import LogScanDao

#
# TESTS UNITAIRES (avec Mocks)
#

mock_dao_instance = MagicMock(spec=LogScanDao)


@patch("service.log_scan_service.LogScanDao", return_value=mock_dao_instance)
def test_enregistrer_log_ok(mock_dao_class):
    """
    Teste que le service crée un objet LogScan
    et appelle le DAO avec.
    """
    mock_dao_instance.reset_mock()
    mock_dao_instance.creer_log.return_value = True
    service = LogScanService(dao=mock_dao_instance)
    params = {
        "id_qrcode": 1,
        "client_host": "3.3.3.3",
        "user_agent": "TestAgent-Service",
        "referer": "http://google.com",
        "accept_language": "en-US",
        "geo_country": "USA",
        "geo_region": "CA",
        "geo_city": "LA",
    }

    log_cree = service.enregistrer_log(**params)

    assert log_cree is not None
    assert isinstance(log_cree, LogScan)
    assert log_cree.client_host == "3.3.3.3"
    assert log_cree.geo_city == "LA"
    mock_dao_instance.creer_log.assert_called_once_with(log_cree)


@patch("service.log_scan_service.LogScanDao", return_value=mock_dao_instance)
def test_enregistrer_log_echec_dao(mock_dao_class):
    """
    Teste le cas où le DAO échoue (retourne False).
    Le service doit alors retourner None.
    """
    mock_dao_instance.reset_mock()
    mock_dao_instance.creer_log.return_value = False
    service = LogScanService(dao=mock_dao_instance)
    log_cree = service.enregistrer_log(id_qrcode=2, client_host="4.4.4.4")
    assert log_cree is None

    mock_dao_instance.creer_log.assert_called_once_with(ANY)
    args, _ = mock_dao_instance.creer_log.call_args
    assert isinstance(args[0], LogScan)


@patch("service.log_scan_service.LogScanDao", return_value=mock_dao_instance)
def test_enregistrer_log_exception_service(mock_dao_class):
    """
    Teste le cas où une exception (ex: BDD) survient dans le DAO
    et que le service la gère (try...except) en retournant None.
    """
    mock_dao_instance.reset_mock()
    mock_dao_instance.creer_log.side_effect = Exception("Erreur BDD simulée")
    service = LogScanService(dao=mock_dao_instance)
    log_cree = service.enregistrer_log(id_qrcode=3, client_host="5.5.5.5")

    assert log_cree is None

    mock_dao_instance.creer_log.assert_called_once_with(ANY)


if __name__ == "__main__":
    pytest.main([__file__])
