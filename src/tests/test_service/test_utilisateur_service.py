from unittest.mock import MagicMock

from service.utilisateur_service import UtilisateurService
from dao.utilisateur_dao import UtilisateurDao
from business_object.utilisateur import Utilisateur

# Liste d'utilisateurs pour les tests
liste_utilisateurs = [
    Utilisateur(id_user="john", mdp="1234"),
    Utilisateur(id_user="marie", mdp="0000"),
    Utilisateur(id_user="paul", mdp="abcd"),
]


def test_creer_user_ok():
    """Création d'Utilisateur réussie"""
    # GIVEN
    id_user, mdp = "john", "1234"
    UtilisateurDao().creer_user = MagicMock(return_value=True)

    # WHEN
    utilisateur = UtilisateurService().creer_user(id_user, mdp)

    # THEN
    assert utilisateur.id_user == id_user


def test_creer_user_echec():
    """Création d'Utilisateur échouée
    (car la méthode UtilisateurDao().creer_user retourne False)"""
    # GIVEN
    id_user, mdp = "john", "1234"
    UtilisateurDao().creer_user = MagicMock(return_value=False)

    # WHEN
    utilisateur = UtilisateurService().creer_user(id_user, mdp)

    # THEN
    assert utilisateur is None


def test_lister_tous_inclure_mdp_true():
    """Lister les Utilisateurs en incluant les mots de passe"""
    # GIVEN
    UtilisateurDao().lister_tous = MagicMock(return_value=liste_utilisateurs)

    # WHEN
    res = UtilisateurService().lister_tous(inclure_mdp=True)

    # THEN
    assert len(res) == 3
    for utilisateur in res:
        assert utilisateur.mdp is not None


def test_lister_tous_inclure_mdp_false():
    """Lister les Utilisateurs en excluant les mots de passe"""
    # GIVEN
    UtilisateurDao().lister_tous = MagicMock(return_value=liste_utilisateurs)

    # WHEN
    res = UtilisateurService().lister_tous()

    # THEN
    assert len(res) == 3
    for utilisateur in res:
        assert utilisateur.mdp is None


def test_trouver_par_id_user_ok():
    """Trouver un utilisateur par son id_user - succès"""
    # GIVEN
    id_user = "marie"
    utilisateur_attendu = Utilisateur(id_user="marie", mdp="0000")
    UtilisateurDao().trouver_par_id_user = MagicMock(return_value=utilisateur_attendu)

    # WHEN
    res = UtilisateurService().trouver_par_id_user(id_user)

    # THEN
    assert res.id_user == id_user
    assert res.mdp == "0000"


def test_trouver_par_id_user_non_trouve():
    """Trouver un utilisateur par son id_user - non trouvé"""
    # GIVEN
    id_user = "inexistant"
    UtilisateurDao().trouver_par_id_user = MagicMock(return_value=None)

    # WHEN
    res = UtilisateurService().trouver_par_id_user(id_user)

    # THEN
    assert res is None


def test_modifier_user_ok():
    """Modification d'un utilisateur réussie"""
    # GIVEN
    utilisateur = Utilisateur(id_user="john", mdp="nouveau_mdp")
    UtilisateurDao().modifier_user = MagicMock(return_value=True)

    # WHEN
    res = UtilisateurService().modifier_user(utilisateur)

    # THEN
    assert res.id_user == "john"
    # Le mot de passe doit être hashé
    assert res.mdp != "nouveau_mdp"  # Il doit être hashé


def test_modifier_user_echec():
    """Modification d'un utilisateur échouée"""
    # GIVEN
    utilisateur = Utilisateur(id_user="john", mdp="nouveau_mdp")
    UtilisateurDao().modifier_user = MagicMock(return_value=False)

    # WHEN
    res = UtilisateurService().modifier_user(utilisateur)

    # THEN
    assert res is None


def test_supprimer_ok():
    """Suppression d'un utilisateur réussie"""
    # GIVEN
    utilisateur = Utilisateur(id_user="paul", mdp="abcd")
    UtilisateurDao().supprimer = MagicMock(return_value=True)

    # WHEN
    res = UtilisateurService().supprimer(utilisateur)

    # THEN
    assert res is True


def test_supprimer_echec():
    """Suppression d'un utilisateur échouée"""
    # GIVEN
    utilisateur = Utilisateur(id_user="inexistant", mdp="test")
    UtilisateurDao().supprimer = MagicMock(return_value=False)

    # WHEN
    res = UtilisateurService().supprimer(utilisateur)

    # THEN
    assert res is False


def test_se_connecter_ok():
    """Connexion d'un utilisateur réussie"""
    # GIVEN
    id_user, mdp = "marie", "0000"
    utilisateur_attendu = Utilisateur(id_user="marie", mdp="hash_0000")
    UtilisateurDao().se_connecter = MagicMock(return_value=utilisateur_attendu)

    # WHEN
    res = UtilisateurService().se_connecter(id_user, mdp)

    # THEN
    assert res.id_user == id_user


def test_se_connecter_echec():
    """Connexion d'un utilisateur échouée (mauvais identifiants)"""
    # GIVEN
    id_user, mdp = "marie", "mauvais_mdp"
    UtilisateurDao().se_connecter = MagicMock(return_value=None)

    # WHEN
    res = UtilisateurService().se_connecter(id_user, mdp)

    # THEN
    assert res is None


def test_id_user_deja_utilise_oui():
    """L'id_user est déjà utilisé dans liste_utilisateurs"""
    # GIVEN
    id_user = "marie"
    UtilisateurDao().lister_tous = MagicMock(return_value=liste_utilisateurs)

    # WHEN
    res = UtilisateurService().id_user_deja_utilise(id_user)

    # THEN
    assert res is True


def test_id_user_deja_utilise_non():
    """L'id_user n'est pas utilisé dans liste_utilisateurs"""
    # GIVEN
    id_user = "nouveau_user"
    UtilisateurDao().lister_tous = MagicMock(return_value=liste_utilisateurs)

    # WHEN
    res = UtilisateurService().id_user_deja_utilise(id_user)

    # THEN
    assert res is False


# Tests supplémentaires spécifiques à votre projet

def test_creation_avec_hashage():
    """Test que le mot de passe est bien hashé lors de la création"""
    # GIVEN
    id_user, mdp_clair = "test_user", "motdepasse123"
    UtilisateurDao().creer_user = MagicMock(return_value=True)

    # WHEN
    utilisateur = UtilisateurService().creer_user(id_user, mdp_clair)

    # THEN
    assert utilisateur.id_user == id_user
    assert utilisateur.mdp != mdp_clair  # Le mdp doit être hashé
    assert len(utilisateur.mdp) > len(mdp_clair)  # Hash généralement plus long


def test_connexion_avec_hashage():
    """Test que le mot de passe est hashé pour la connexion"""
    # GIVEN
    id_user, mdp_clair = "marie", "0000"
    utilisateur_avec_hash = Utilisateur(id_user="marie", mdp="hash_de_0000")
    
    # Mock de la fonction hash_password pour contrôler le résultat
    import service.utilisateur_service as service_module
    service_module.hash_password = MagicMock(return_value="hash_de_0000")
    
    UtilisateurDao().se_connecter = MagicMock(return_value=utilisateur_avec_hash)

    # WHEN
    res = UtilisateurService().se_connecter(id_user, mdp_clair)

    # THEN
    assert res is not None
    assert res.id_user == id_user
    # Vérifier que hash_password a été appelé avec les bons paramètres
    service_module.hash_password.assert_called_with(mdp_clair, id_user)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])