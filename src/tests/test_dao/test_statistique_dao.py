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
    assert isinstance(s.id_stat, int) and s.id_stat > 0

    # Vérifier existence par id
    s_db = StatistiqueDao().trouver_par_id_qrcode(s.id_qrcode)
    assert s_db is not None
    assert s_db.id_qrcode == id_qr

def test_creer_stat_ko():
    """Création échouée si données invalides"""
    # données manquantes
    s = Statistique(id_qrcode=None, nombre_vue=None, date_des_vues=None)
    ok = StatistiqueDao().creer_statistique(s)
    assert ok is False

def test_trouver_par_id_stat_existant():
    """Recherche par id_stat d'une statistique existant"""
    # On crée une stat pour être sûr de l’existence
    id_qrcode = randint(1,9999)
    nombre_vue = 2
    date_des_vues = [date(2025,10,21), date(2025,11,3)]
    s = Statistique(id_qrcode=id_qrcode, nombre_vue= nombre_vue, date_des_vues=date_des_vues)
    StatistiqueDao().creer_statistique(s)

    statistique = StatistiqueDao().trouver_par_id_stat(s.id_stat)
    assert statistique is not None
    assert isinstance(statistique, Statistique)
    assert statistique.id_qrcode == s.id_qrcode
    assert statistique.id_stat == s.id_stat


def test_trouver_par_id_stat_non_existant():
    """Recherche par id_user inexistant"""
    statistique = StatistiqueDao().trouver_par_id_stat(999999)
    assert statistique is None

def test_modifier_stat_ok():
    """Modification"""
    # Crée une statistique
    id_qrcode = randint(1,9999)
    nbr_vue = 2
    date_des_vues = [date(2025,10,21), date(2025,11,2)]
    s = Statistique(id_qrcode=id_qrcode, nombre_vue=nbr_vue, date_des_vues=date_des_vues)
    StatistiqueDao().creer_statistique(s)

    # Modifie son nbr_vue et date_des_vues
    s._nombre_vue += 1
    date_des_vues = date_des_vues.append(date(2025,11,5))
    assert StatistiqueDao().modifier_statistique(s) is not None

    # Vérifier en base
    s_db = StatistiqueDao().trouver_par_id_stat(s.id_stat)
    assert s_db is not None
    assert s_db == 3
    assert s_db.date_des_vues == [date(2025,10,21), date(2025,11,2), date(2025,11,5)]

def test_modifier_stat_ko():
    """Modification échouée (id_qrcode inexistant)"""
    s = Statistique(id_qrcode=999999, nombre_vue=1, date_des_vues=[date(2025,11,2)])
    ok = StatistiqueDao().modifier_statistique(s)
    assert ok is False

def test_supprimer_ok():
    """Suppression réussie"""
    nom_user = "to_delete"
    u = Utilisateur(nom_user=nom_user, mdp=hash_password("pwd", nom_user))
    UtilisateurDao().creer_user(u)

    ok = UtilisateurDao().supprimer(u)
    assert ok is True
    assert UtilisateurDao().trouver_par_id_user(u.id_user) is None

def test_supprimer_ko():
    """Suppression échouée (id inexistant)"""
    u = Utilisateur(id_user=999999, nom_user="ghost", mdp="irrelevant")
    ok = UtilisateurDao().supprimer(u)
    assert ok is False
