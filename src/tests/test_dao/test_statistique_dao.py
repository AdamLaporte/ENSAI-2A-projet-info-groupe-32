import os
import pytest
from datetime import date
from unittest.mock import patch

from utils.reset_database import ResetDatabase
from dao.statistique_dao import StatistiqueDao
from business_object.statistique import Statistique # Gardé pour le test de suppression

#
# SETUP DE TEST (Corrigé avec scope="function")
#
@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """
    Initialise une base dédiée aux tests.
    Scope="function" : la base est réinitialisée AVANT CHAQUE TEST.
    """
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        # Assure-toi que pop_db_test.sql contient les données pour les QR 1, 2, 3
        ResetDatabase().lancer(test_dao=True)
    yield

#
# TESTS DE LA NOUVELLE LOGIQUE (Tests Ajoutés)
#

def test_incrementer_vue_jour():
    """
    Teste que l'UPSERT de incrementer_vue_jour fonctionne.
    On ajoute 2 vues à une date qui n'existe pas encore.
    """
    dao = StatistiqueDao()
    id_qr_test = 1 # Doit exister dans pop_db_test.sql
    date_test = date(2025, 11, 1) # Date non présente dans pop_db_test

    # 1. Première vue à cette date (INSERT)
    ok1 = dao.incrementer_vue_jour(id_qr_test, date_test)
    assert ok1 is True

    # 2. Deuxième vue à cette date (UPDATE)
    ok2 = dao.incrementer_vue_jour(id_qr_test, date_test)
    assert ok2 is True

    # 3. Vérification
    stats_jour = dao.get_stats_par_jour(id_qr_test)
    
    # Trouve l'entrée pour notre date de test
    entree_test = next((s for s in stats_jour if s["date_des_vues"] == date_test), None)
    
    assert entree_test is not None
    assert entree_test["nombre_vue"] == 2

def test_get_agregats_ok():
    """
    Teste la récupération des agrégats pour un QR code
    basé sur les données de pop_db_test.sql.
    QR 1 a 2 entrées : (0 vues, 2025-10-01) et (5 vues, 2025-10-02)
   
    """
    dao = StatistiqueDao()
    id_qr_test = 1
    
    agregats = dao.get_agregats(id_qr_test)
    
    assert agregats is not None
    assert agregats["total_vues"] == 5 # 0 + 5
    assert agregats["premiere_vue"] == date(2025, 10, 1)
    assert agregats["derniere_vue"] == date(2025, 10, 2)

def test_get_agregats_aucun_resultat():
    """
    Teste les agrégats pour un QR code qui n'a aucune stat.
    """
    dao = StatistiqueDao()
    id_qr_inexistant = 999
    
    agregats = dao.get_agregats(id_qr_inexistant)
    
    assert agregats is not None
    assert agregats["total_vues"] == 0
    assert agregats["premiere_vue"] is None
    assert agregats["derniere_vue"] is None

def test_get_stats_par_jour_ok():
    """
    Teste la récupération de l'historique par jour (basé sur pop_db_test.sql)
    """
    dao = StatistiqueDao()
    id_qr_test = 1
    
    historique = dao.get_stats_par_jour(id_qr_test)
    
    assert isinstance(historique, list)
    assert len(historique) == 2 # 2 jours de stats pour QR 1
    assert historique[0]["date_des_vues"] == date(2025, 10, 1)
    assert historique[0]["nombre_vue"] == 0
    assert historique[1]["date_des_vues"] == date(2025, 10, 2)
    assert historique[1]["nombre_vue"] == 5

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])