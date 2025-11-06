import os 
import pytest 
from datetime import date 
from random import randint
from unittest.mock import patch 
from utils.reset_database import ResetDatabase 
from dao.statistique_dao import StatistiqueDao 
from business_object.statistique import Statistique

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test pour StatistiqueDao"""
    # On force le schéma de tests via la variable utilisée par le code
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
    yield

def test_lister_toutes():
    """La méthode renvoie une liste de Utilisateur de taille ≥ 2"""
    statistiques = StatistiqueDao().lister_toutes()
    assert isinstance(statistiques, list)
    assert all(isinstance(s, Statistique) for s in statistiques)
    assert len(statistiques) >= 2

def test_creer_stat_ok():
    """Création d'une statistique réussie avec id auto-généré"""
    id_qr = randint(1,9999)
    nbr_vue = 2
    dates = [date(2025,10,21), date(2025,11,3)]
    s = Statistique(id_qrcode=id_qr, nombre_vue=nbr_vue, date_des_vues=date)

    ok = StatistiqueDao().creer_statistique(s)
    assert ok is True
    assert isinstance(s.id_stat, int) and u.id_stat > 0

    # Vérifier existence par id
    s_db = StatistiqueDao().trouver_par_id_qrcode(s.id_qrcode)
    assert s_db is not None
    assert s_db.id_qrcode == id_qr