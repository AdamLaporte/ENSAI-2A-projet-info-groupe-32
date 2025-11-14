from unittest.mock import MagicMock, patch
from datetime import date, datetime
from service.statistique_service import StatistiqueService
import pytest
from dao.statistique_dao import StatistiqueDao
from dao.log_scan_dao import LogScanDao


def test_enregistrer_vue():
    """
    Teste que le service 'enregistrer_vue' appelle bien
    la méthode 'incrementer_vue_jour' du DAO.
    """
    with patch.object(StatistiqueDao, 'incrementer_vue_jour', return_value=True) as mock_increment:
        service = StatistiqueService()
        id_qr = 1
        date_test = date(2025, 10, 1)
        
        resultat = service.enregistrer_vue(id_qr, date_test)
        
        assert resultat is True
        mock_increment.assert_called_once_with(id_qr, date_test)

def test_get_statistiques_qr_code_detail_complet():
    """
    Teste l'orchestration de 'get_statistiques_qr_code' avec detail=True.
    Le service doit appeler les 3 méthodes DAO et agréger les résultats.
    """
    # 1. Préparer les Mocks
    mock_agregats = {"total_vues": 10, "premiere_vue": date(2025, 1, 1), "derniere_vue": date(2025, 1, 5)}
    mock_par_jour = [{"date_des_vues": date(2025, 1, 1), "nombre_vue": 10}]
    mock_scans_recents = [{
        "date_scan": datetime(2025, 1, 1, 12, 30, 0),
        "client_host": "1.2.3.4",
        "user_agent": "TestAgent",
        "referer": None,
        "accept_language": "fr-FR",
        "geo_country": "France",
        "geo_region": "Bretagne",
        "geo_city": "Rennes"
    }]

    # 2. Patcher les méthodes DAO
    # Note: On patche les méthodes sur les classes importées dans le module service
    with patch('service.statistique_service.StatistiqueDao.get_agregats', return_value=mock_agregats) as mock_get_agg, \
         patch('service.statistique_service.StatistiqueDao.get_stats_par_jour', return_value=mock_par_jour) as mock_get_jour, \
         patch('service.statistique_service.LogScanDao.get_scans_recents', return_value=mock_scans_recents) as mock_get_logs:

        # 3. Appeler le service
        service = StatistiqueService()
        resultat = service.get_statistiques_qr_code(id_qrcode=1, detail=True)
        
        # 4. Vérifier les appels
        mock_get_agg.assert_called_once_with(1)
        mock_get_jour.assert_called_once_with(1)
        mock_get_logs.assert_called_once_with(1)
        
        # 5. Vérifier le résultat
        assert resultat["id_qrcode"] == 1
        assert resultat["total_vues"] == 10
        assert resultat["premiere_vue"] == "2025-01-01" # Conversion en ISO string
        assert len(resultat["par_jour"]) == 1
        assert resultat["par_jour"][0]["vues"] == 10
        assert len(resultat["scans_recents"]) == 1
        assert resultat["scans_recents"][0]["geo_city"] == "Rennes"

def test_get_statistiques_qr_code_no_detail():
    """
    Teste 'get_statistiques_qr_code' avec detail=False.
    Le service NE DOIT PAS appeler get_stats_par_jour et get_scans_recents.
    """
    mock_agregats = {"total_vues": 10, "premiere_vue": date(2025, 1, 1), "derniere_vue": date(2025, 1, 5)}

    with patch('service.statistique_service.StatistiqueDao.get_agregats', return_value=mock_agregats) as mock_get_agg, \
         patch('service.statistique_service.StatistiqueDao.get_stats_par_jour') as mock_get_jour, \
         patch('service.statistique_service.LogScanDao.get_scans_recents') as mock_get_logs:

        service = StatistiqueService()
        resultat = service.get_statistiques_qr_code(id_qrcode=1, detail=False)
        
        # Seul get_agregats doit être appelé
        mock_get_agg.assert_called_once_with(1)
        mock_get_jour.assert_not_called()
        mock_get_logs.assert_not_called()
        
        # Le résultat ne contient pas les clés de détail
        assert "par_jour" not in resultat
        assert "scans_recents" not in resultat
        assert resultat["total_vues"] == 10

def test_get_statistiques_qr_code_no_data():
    """
    Teste le cas où 'get_agregats' retourne None (ou 0 vues).
    Le service doit retourner une structure valide avec 0.
    """
    # get_agregats retourne None si le QR n'est pas trouvé
    mock_agregats = None 

    with patch('service.statistique_service.StatistiqueDao.get_agregats', return_value=mock_agregats) as mock_get_agg, \
         patch('service.statistique_service.StatistiqueDao.get_stats_par_jour', return_value=[]) as mock_get_jour, \
         patch('service.statistique_service.LogScanDao.get_scans_recents', return_value=[]) as mock_get_logs:

        service = StatistiqueService()
        resultat = service.get_statistiques_qr_code(id_qrcode=999, detail=True)
        
        mock_get_agg.assert_called_once_with(999)
        
        assert resultat["id_qrcode"] == 999
        assert resultat["total_vues"] == 0
        assert resultat["premiere_vue"] is None
        assert resultat["derniere_vue"] is None
        assert resultat["par_jour"] == []
        assert resultat["scans_recents"] == []

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])