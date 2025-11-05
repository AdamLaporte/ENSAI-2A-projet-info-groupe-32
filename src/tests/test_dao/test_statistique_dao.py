import os
import pytest
from datetime import date
from unittest.mock import patch

from utils.reset_database import ResetDatabase
from dao.statistique_dao import StatistiqueDao
from business_object.statistique import Statistique


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation du schéma de tests pour StatistiqueDao"""
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
    yield


def test_lister_tous():
    """La méthode renvoie une liste de Statistique de taille ≥ 1"""
    statistiques = StatistiqueDao().lister_tous()
    assert isinstance(statistiques, list)
    assert all(isinstance(s, Statistique) for s in statistiques)
    for s in statistiques:
        assert s.nombre_vue == len(s.date_des_vues)


def test_creer_statistique_ok():
    """Création réussie avec cohérence nombre_vue == len(date_des_vues)"""
    dates = [date(2025, 10, 24), date(2025, 10, 25)]
    s = Statistique(id_qrcode=10, nombre_vue=len(dates), date_des_vues=dates)

    ok = StatistiqueDao().creer_statistique(s)
    assert ok is True
    assert isinstance(s.id_qrcode, int)
    assert s.nombre_vue == len(s.date_des_vues)

    # Vérifie que la statistique est bien retrouvée
    s_db = StatistiqueDao().trouver_par_id_qrcode(s.id_qrcode)
    assert s_db is not None
    assert isinstance(s_db, Statistique)
    assert s_db.id_qrcode == s.id_qrcode
    assert s_db.nombre_vue == len(s_db.date_des_vues)


def test_creer_statistique_ko():
    """Création échouée si incohérence entre nombre_vue et date_des_vues"""
    dates = [date(2025, 10, 25)]
    s = Statistique(id_qrcode=11, nombre_vue=5, date_des_vues=dates) 

    ok = StatistiqueDao().creer_statistique(s)
    assert ok is False


def test_trouver_par_id_qrcode_existant():
    """Recherche d'une statistique existante par id_qrcode"""
    dates = [date(2025, 10, 22), date(2025, 10, 23)]
    s = Statistique(id_qrcode=12, nombre_vue=len(dates), date_des_vues=dates)
    StatistiqueDao().creer_statistique(s)

    s_db = StatistiqueDao().trouver_par_id_qrcode(s.id_qrcode)
    assert s_db is not None
    assert isinstance(s_db, Statistique)
    assert s_db.id_qrcode == s.id_qrcode
    assert s_db.nombre_vue == len(s_db.date_des_vues)


def test_trouver_par_id_qrcode_non_existant():
    """Recherche d'une statistique inexistante"""
    s = StatistiqueDao().trouver_par_id_qrcode(999999)
    assert s is None


def test_modifier_statistique_ok():
    """Modification réussie : ajout d'une date de vue"""
    dates_init = [date(2025, 10, 21)]
    s = Statistique(id_qrcode=13, nombre_vue=len(dates_init), date_des_vues=dates_init)
    StatistiqueDao().creer_statistique(s)

    s.date_des_vues.append(date(2025, 10, 22))
    s.nombre_vue = len(s.date_des_vues)

    ok = StatistiqueDao().modifier_statistique(s)
    assert ok is True

    s_db = StatistiqueDao().trouver_par_id_qrcode(s.id_qrcode)
    assert s_db.nombre_vue == len(s_db.date_des_vues)
    assert date(2025, 10, 22) in s_db.date_des_vues


def test_modifier_statistique_ko():
    """Modification échouée (id_qrcode inexistant)"""
    dates = [date(2025, 10, 25)]
    s = Statistique(id_qrcode=999999, nombre_vue=len(dates), date_des_vues=dates)
    ok = StatistiqueDao().modifier_statistique(s)
    assert ok is False


def test_supprimer_ok():
    """Suppression réussie"""
    dates = [date(2025, 10, 20)]
    s = Statistique(id_qrcode=14, nombre_vue=len(dates), date_des_vues=dates)
    StatistiqueDao().creer_statistique(s)

    ok = StatistiqueDao().supprimer(s)
    assert ok is True
    assert StatistiqueDao().trouver_par_id_qrcode(s.id_qrcode) is None


def test_supprimer_ko():
    """Suppression échouée (id_qrcode inexistant)"""
    s = Statistique(id_qrcode=999999, nombre_vue=0, date_des_vues=[])
    ok = StatistiqueDao().supprimer(s)
    assert ok is False


def test_sauvegarde_et_relecture_dates():
    """Vérifie la persistance fidèle de la liste de dates"""
    dates = [date(2025, 10, 21), date(2025, 10, 22), date(2025, 10, 23)]
    s = Statistique(id_qrcode=15, nombre_vue=len(dates), date_des_vues=dates)

    StatistiqueDao().creer_statistique(s)
    s_db = StatistiqueDao().trouver_par_id_qrcode(s.id_qrcode)

    assert isinstance(s_db.date_des_vues, list)
    assert all(isinstance(d, date) for d in s_db.date_des_vues)
    assert s_db.date_des_vues == dates
    assert s_db.nombre_vue == len(s_db.date_des_vues)


if __name__ == "__main__":
    pytest.main([__file__])
