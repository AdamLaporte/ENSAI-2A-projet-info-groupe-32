import os

import pytest

from unittest.mock import patch

from utils.reset_database import ResetDatabase

from utils.securite import hash_password

from dao.utilisateur_dao import UtilisateurDao

from business_object.utilisateur import Utilisateur

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test pour UtilisateurDao"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
    yield


def test_trouver_par_id_user_existant():
    """Recherche par id_user d'un utilisateur existant"""
    # GIVEN
    id_user = "user_001"
    # WHEN
    utilisateur = UtilisateurDao().trouver_par_id_user(id_user)
    # THEN
    assert utilisateur is not None
    assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.id_user == id_user


def test_trouver_par_id_user_non_existant():
    """Recherche par id_user d'un utilisateur n'existant pas"""
    # GIVEN
    id_user = "inexistant"
    # WHEN
    utilisateur = UtilisateurDao().trouver_par_id_user(id_user)
    # THEN
    assert utilisateur is None


def test_lister_tous():
    """Vérifie que la méthode renvoie une liste de Utilisateur de taille ≥ 2"""
    # WHEN
    utilisateurs = UtilisateurDao().lister_tous()
    # THEN
    assert isinstance(utilisateurs, list)
    assert all(isinstance(u, Utilisateur) for u in utilisateurs)
    assert len(utilisateurs) >= 2


def test_creer_user_ok():
    """Création d'Utilisateur réussie"""
    # GIVEN
    utilisateur = Utilisateur(id_user="temp_user", mdp=hash_password("pwd", "temp_user"))
    # WHEN
    creation_ok = UtilisateurDao().creer_user(utilisateur)
    # THEN
    assert creation_ok
    # id_user est clé primaire fournie, on vérifie existence
    u = UtilisateurDao().trouver_par_id_user("temp_user")
    assert u is not None


def test_creer_user_ko():
    """Création échouée (id_user None)"""
    # GIVEN
    utilisateur = Utilisateur(id_user=None, mdp=None)
    # WHEN
    creation_ok = UtilisateurDao().creer_user(utilisateur)
    # THEN
    assert not creation_ok


def test_modifier_user_ok():
    """Modification d'un utilisateur réussie"""
    # GIVEN
    existing = UtilisateurDao().lister_tous()[0]
    existing.mdp = hash_password("new_pwd", existing.id_user)
    # WHEN
    modification_ok = UtilisateurDao().modifier_user(existing)
    # THEN
    assert modification_ok
    # vérifier en base
    u = UtilisateurDao().trouver_par_id_user(existing.id_user)
    assert u.mdp == existing.mdp


def test_modifier_user_ko():
    """Modification échouée (id_user inexistant)"""
    # GIVEN
    utilisateur = Utilisateur(id_user="no_user", mdp=hash_password("pwd", "no_user"))
    # WHEN
    modification_ok = UtilisateurDao().modifier_user(utilisateur)
    # THEN
    assert not modification_ok


def test_supprimer_ok():
    """Suppression d'un utilisateur réussie"""
    # GIVEN
    user = Utilisateur(id_user="to_delete", mdp=hash_password("pwd", "to_delete"))
    UtilisateurDao().creer_user(user)
    # WHEN
    suppression_ok = UtilisateurDao().supprimer(user)
    # THEN
    assert suppression_ok
    assert UtilisateurDao().trouver_par_id_user("to_delete") is None


def test_supprimer_ko():
    """Suppression échouée (id_user inexistant)"""
    # GIVEN
    utilisateur = Utilisateur(id_user="ghost", mdp="irrelevant")
    # WHEN
    suppression_ok = UtilisateurDao().supprimer(utilisateur)
    # THEN
    assert not suppression_ok


def test_se_connecter_ok():
    """Connexion d'un utilisateur réussie"""
    # GIVEN
    id_user = "auth_user"
    mdp_clair = "secret"
    hashed = hash_password(mdp_clair, id_user)
    user = Utilisateur(id_user=id_user, mdp=hashed)
    UtilisateurDao().creer_user(user)
    # WHEN
    res = UtilisateurDao().se_connecter(id_user, hashed)
    # THEN
    assert isinstance(res, Utilisateur)
    assert res.id_user == id_user


def test_se_connecter_ko():
    """Connexion échouée (mauvais mdp)"""
    # GIVEN
    id_user = "auth_user2"
    mdp_clair = "secret2"
    hashed = hash_password(mdp_clair, id_user)
    UtilisateurDao().creer_user(Utilisateur(id_user=id_user, mdp=hashed))
    # WHEN
    res = UtilisateurDao().se_connecter(id_user, hash_password("wrong", id_user))
    # THEN
    assert res is None

if __name__ == "__main__":
    pytest.main([__file__])