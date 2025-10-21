import os
import pytest
from unittest.mock import patch

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from dao.utilisateur_dao import UtilisateurDao
from business_object.utilisateur import Utilisateur
from service.utilisateur_service import UtilisateurService

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test pour UtilisateurDao"""
    # On force le schéma de tests via la variable utilisée par le code
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
    yield

def test_lister_tous():
    """La méthode renvoie une liste de Utilisateur de taille ≥ 2"""
    utilisateurs = UtilisateurDao().lister_tous()
    assert isinstance(utilisateurs, list)
    assert all(isinstance(u, Utilisateur) for u in utilisateurs)
    assert len(utilisateurs) >= 2

def test_creer_user_ok():
    """Création d'utilisateur réussie avec id auto-généré"""
    nom_user = "temp_user"
    mdp_h = hash_password("pwd", nom_user)
    u = Utilisateur(nom_user=nom_user, mdp=mdp_h)

    ok = UtilisateurDao().creer_user(u)
    assert ok is True
    assert isinstance(u.id_user, int) and u.id_user > 0

    # Vérifier existence par id
    u_db = UtilisateurDao().trouver_par_id_user(u.id_user)
    assert u_db is not None
    assert u_db.nom_user == nom_user

def test_creer_user_ko():
    """Création échouée si données invalides"""
    # nom_user manquant et mdp manquant
    u = Utilisateur(nom_user=None, mdp=None)
    ok = UtilisateurDao().creer_user(u)
    assert ok is False

def test_trouver_par_id_user_existant():
    """Recherche par id_user d'un utilisateur existant"""
    # On crée un utilisateur pour être sûr de l’existence
    nom_user = "user_001"
    mdp_h = hash_password("pwd", nom_user)
    u = Utilisateur(nom_user=nom_user, mdp=mdp_h)
    UtilisateurDao().creer_user(u)

    utilisateur = UtilisateurDao().trouver_par_id_user(u.id_user)
    assert utilisateur is not None
    assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.id_user == u.id_user
    assert utilisateur.nom_user == nom_user

def test_trouver_par_id_user_non_existant():
    """Recherche par id_user inexistant"""
    utilisateur = UtilisateurDao().trouver_par_id_user(999999)
    assert utilisateur is None

def test_trouver_par_nom_user_ok():
    """Recherche par nom_user (login)"""
    nom_user = "lookup_user"
    mdp_h = hash_password("pwd", nom_user)
    u = Utilisateur(nom_user=nom_user, mdp=mdp_h)
    UtilisateurDao().creer_user(u)

    u_db = UtilisateurDao().trouver_par_nom_user(nom_user)
    assert u_db is not None
    assert u_db.nom_user == nom_user
    assert isinstance(u_db.id_user, int)

def test_modifier_user_ok():
    """Modification (rehash déjà faite au niveau service)"""
    # Crée un utilisateur
    nom_user = "john_mod"
    u = Utilisateur(nom_user=nom_user, mdp=hash_password("old", nom_user))
    UtilisateurDao().creer_user(u)

    # Modifie son mdp via service pour appliquer le hash avec nom_user
    u.mdp = "new_pwd"
    assert UtilisateurService().modifier_user(u) is not None

    # Vérifier en base
    u_db = UtilisateurDao().trouver_par_id_user(u.id_user)
    assert u_db is not None
    assert u_db.mdp != "new_pwd"  # bien hashé

def test_modifier_user_ko():
    """Modification échouée (id_user inexistant)"""
    u = Utilisateur(id_user=999999, nom_user="no_user", mdp=hash_password("pwd", "no_user"))
    ok = UtilisateurDao().modifier_user(u)
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

def test_se_connecter_ok():
    """Connexion par nom_user + mdp hashé"""
    nom_user = "auth_user"
    mdp_clair = "secret"
    mdp_hash = hash_password(mdp_clair, nom_user)

    # provision
    u = Utilisateur(nom_user=nom_user, mdp=mdp_hash)
    UtilisateurDao().creer_user(u)

    # login
    res = UtilisateurDao().se_connecter(nom_user, mdp_hash)
    assert isinstance(res, Utilisateur)
    assert res.nom_user == nom_user

def test_se_connecter_ko():
    """Connexion échouée (mauvais mdp)"""
    nom_user = "auth_user2"
    real_hash = hash_password("secret2", nom_user)
    UtilisateurDao().creer_user(Utilisateur(nom_user=nom_user, mdp=real_hash))

    bad_hash = hash_password("wrong", nom_user)
    res = UtilisateurDao().se_connecter(nom_user, bad_hash)
    assert res is None

if __name__ == "__main__":
    pytest.main([__file__])