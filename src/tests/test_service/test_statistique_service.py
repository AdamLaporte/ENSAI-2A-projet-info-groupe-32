from unittest.mock import MagicMock
from datetime import date 
from random import randint
from service.statistique_service import StatistiqueService
from dao.statistique_dao import StatistiqueDao
from business_object.statistique import Statistique

# Liste de statistiques pour les tests
liste_statistiques = [
    Statistique(id_qrcode=1234, nombre_vue=1, date_des_vues = [date(2025,10,1)]),
    Statistique(id_qrcode=5678, nombre_vue=2, date_des_vues = [date(2025,10,21), date(2025,9,25)]),
    Statistique(id_qrcode=9999, nombre_vue=7, date_des_vues = [date(2025,8,17),date(2025,9,27), date(2025,10,19)]),
]

def test_creer_statistique_ok():
    """Création d'une Statistique réussie"""
    # GIVEN
    id_qrcode, nombre_vue, date_des_vues = randint(1,9999), 1, [date(randint(1994,2025),randint(1,12),randint(1,28))]
    StatistiqueDao().creer_statistique = MagicMock(return_value=True)

    # WHEN
    statistique = StatistiqueService().creer_statistique(id_qrcode, nombre_vue, date_des_vues)

    # THEN
    assert statistique.id_qrcode == id_qrcode
    assert statistique.nombre_vue == nombre_vue
    assert statistique.date_des_vues == date_des_vues

def test_creer_statistique_echec():
    """Création d'une Statistique échouée (DAO retourne False)"""
    # GIVEN
    id_qrcode, nombre_vue, date_des_vues = randint(1,9999), 2, [date(randint(1994,2025),randint(1,12),randint(1,28))]
    StatistiqueDao().creer_statistique = MagicMock(return_value=False)

    # WHEN
    statistique = StatistiqueService().creer_statistique(id_qrcode, nombre_vue, date_des_vues)

    # THEN
    assert statistique is None

def test_lister_tous():
    """Lister toutes les statistiques"""
    # GIVEN
    StatistiqueDao().lister_tous = MagicMock(return_value=liste_statistiques)

    # WHEN
    res = StatistiqueService().lister_tous()

    # THEN
    assert len(res) == 3
    assert all(isinstance(s, Statistique) for s in res)

def test_trouver_par_id_qrcode_ok():
    """Trouver une statistique par id_qrcode - succès"""
    # GIVEN
    id_qrcode = randint(1,9999)
    statistique_attendue = Statistique(id_qrcode, nombre_vue=1, date_des_vues=[date(2025,10,21)])
    StatistiqueDao().trouver_par_id_qrcode = MagicMock(return_value=statistique_attendue)

    # WHEN
    res = StatistiqueService().trouver_par_id_qrcode(id_qrcode)

    # THEN
    assert res.id_qrcode == id_qrcode
    assert res.nombre_vue == 1

def test_trouver_par_id_qrcode_non_trouve():
    """Trouver une statistique par id_qrcode - non trouvé"""
    # GIVEN
    id_qrcode = "inexistant"
    StatistiqueDao().trouver_par_id_qrcode = MagicMock(return_value=None)

    # WHEN
    res = StatistiqueService().trouver_par_id_qrcode(id_qrcode)

    # THEN
    assert res is None

def test_modifier_statistique_ok():
    """Modification d'une statistique réussie"""
    # GIVEN
    statistique = Statistique(id_qrcode=randint(1,9999), nombre_vue=1, date_des_vues=[date(2025,10,10)])
    StatistiqueDao().modifier_statistique = MagicMock(return_value=True)

    # WHEN
    res = StatistiqueService().modifier_statistique(statistique)

    # THEN
    assert res.nombre_vue == 1
    assert res.date_des_vues == [date(2025,10,10)]

def test_modifier_statistique_echec():
    """Modification d'une statistique échouée"""
    # GIVEN
    statistique = Statistique(id_qrcode=randint(1,9999), nombre_vue=1, date_des_vues=[date(2025,10,10)])
    StatistiqueDao().modifier_statistique = MagicMock(return_value=False)

    # WHEN
    res = StatistiqueService().modifier_statistique(statistique)

    # THEN
    assert res is None

def test_supprimer_ok():
    """Suppression d'une statistique réussie"""
    # GIVEN
    statistique = Statistique(id_qrcode=randint(1,9999), nombre_vue=7, date_des_vues=[date(2025,10,10)])
    StatistiqueDao().supprimer = MagicMock(return_value=True)

    # WHEN
    res = StatistiqueService().supprimer(statistique)

    # THEN
    assert res is True

def test_supprimer_echec():
    """Suppression d'une statistique échouée"""
    # GIVEN
    statistique = Statistique(id_qrcode=randint(1,9999), nombre_vue=0, date_des_vues=[date(2025,10,20)])
    StatistiqueDao().supprimer = MagicMock(return_value=False)

    # WHEN
    res = StatistiqueService().supprimer(statistique)

    # THEN
    assert res is False

def test_id_qrcode_deja_utilise_oui():
    """id_qrcode déjà utilisé"""
    # GIVEN
    id_qrcode = 1234
    StatistiqueDao().lister_tous = MagicMock(return_value=liste_statistiques)

    # WHEN
    res = StatistiqueService().id_qrcode_deja_utilise(id_qrcode)

    # THEN
    assert res is True

def test_id_qrcode_deja_utilise_non():
    """id_qrcode non utilisé"""
    # GIVEN
    id_qrcode = "nouveau_qrcode"
    StatistiqueDao().lister_tous = MagicMock(return_value=liste_statistiques)

    # WHEN
    res = StatistiqueService().id_qrcode_deja_utilise(id_qrcode)

    # THEN
    assert res is False

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
