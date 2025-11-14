import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Assure que le PYTHONPATH est correct pour importer 'app'
# (pytest gère ça, mais c'est pour la clarté)
from app import app 
from utils.reset_database import ResetDatabase

#
# ----------------- FIXTURES (outils de test) -----------------
#

@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """
    Fixture auto-exécutée AVANT CHAQUE TEST.
    Patche l'OS pour utiliser le schéma de test, puis réinitialise
    la base de données de test (via pop_db_test.sql).
    """
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
    yield

@pytest.fixture(scope="function")
def client():
    """
    Fournit un client de test FastAPI pour chaque test.
    """
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def auth_headers_user1(client):
    """
    Fixture qui se connecte en tant que 'test_u1' (de pop_db_test.sql)
    et retourne les headers d'authentification valides.
    """
    response = client.post(
        "/login",
        data={"username": "test_u1", "password": "test_u1"}
    )
    assert response.status_code == 200, "Échec de la connexion pour le setup de test"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def auth_headers_user2(client):
    """
    Fixture qui se connecte en tant que 'test_u2' (de pop_db_test.sql)
    et retourne les headers d'authentification valides.
    """
    response = client.post(
        "/login",
        data={"username": "test_u2", "password": "test_u2"}
    )
    assert response.status_code == 200, "Échec de la connexion pour le setup de test"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

#
# ----------------- TESTS DES ROUTES -----------------
#

### 1. Routes d'Authentification (Publiques)

def test_register_ok(client):
    """Teste la création réussie d'un nouveau compte."""
    response = client.post(
        "/register",
        json={"nom_user": "new_user_api", "mdp": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nom_user"] == "new_user_api"
    assert "id_user" in data

def test_register_user_exists(client):
    """Teste l'échec si le nom d'utilisateur est déjà pris."""
    response = client.post(
        "/register",
        json={"nom_user": "test_u1", "mdp": "password123"} # test_u1 existe
    )
    assert response.status_code == 400
    assert "déjà utilisé" in response.json()["detail"]

def test_login_ok(client):
    """Teste une connexion réussie avec des identifiants valides."""
    response = client.post(
        "/login",
        data={"username": "test_u1", "password": "test_u1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_fail_password(client):
    """Teste l'échec de connexion (mauvais mot de passe)."""
    response = client.post(
        "/login",
        data={"username": "test_u1", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"]

def test_login_fail_user(client):
    """Teste l'échec de connexion (utilisateur inconnu)."""
    response = client.post(
        "/login",
        data={"username": "unknown_user", "password": "password"}
    )
    assert response.status_code == 401

### 2. Route de Scan (Publique)

def test_scan_ok_tracked(client):
    """Teste le scan d'un QR 'suivi' (id=1). Doit rediriger (307)."""
    # On désactive les redirections pour inspecter la 1ère réponse
    response = client.get("/scan/1", follow_redirects=False)
    assert response.status_code == 307
    # Vérifie que la redirection pointe vers la bonne URL de destination
    assert response.headers["location"] == "https://t.local/u1/a"

def test_scan_ok_not_tracked(client):
    """Teste le scan d'un QR 'non-suivi' (id=2). Doit rediriger (307)."""
    response = client.get("/scan/2", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://t.local/u2/b"

def test_scan_not_found(client):
    """Teste le scan d'un QR code inexistant."""
    response = client.get("/scan/999", follow_redirects=False)
    assert response.status_code == 404

### 3. Routes QR Code (Protégées)

def test_get_my_qrcodes_unauthorized(client):
    """Teste l'accès aux QR codes sans token."""
    response = client.get("/qrcode/utilisateur/me")
    assert response.status_code == 401 # Unauthorized

def test_get_my_qrcodes_ok(client, auth_headers_user1):
    """Teste l'accès aux QR codes avec un token valide."""
    response = client.get("/qrcode/utilisateur/me", headers=auth_headers_user1)
    assert response.status_code == 200
    data = response.json()
    # 'test_u1' a 1 QR code dans pop_db_test.sql
    assert len(data) == 1
    assert data[0]["id_qrcode"] == 1
    assert data[0]["url"] == "https://t.local/u1/a"

def test_create_qrcode_ok(client, auth_headers_user1):
    """Teste la création d'un QR code en étant authentifié."""
    payload = {
        "url": "https://www.nouveau-site.com",
        "id_proprietaire": "1", # Cet ID sera écrasé par celui du token
        "type_qrcode": True
    }
    response = client.post("/qrcode/", headers=auth_headers_user1, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://www.nouveau-site.com"
    assert data["id_proprietaire"] == "1" # Vérifie que le QR est bien lié à user 1
    assert "scan_url" in data # Preuve que c'est un QR suivi

def test_delete_qrcode_unauthorized(client):
    """Teste la suppression sans token."""
    response = client.delete("/qrcode/1")
    assert response.status_code == 401

def test_delete_qrcode_not_owner(client, auth_headers_user2):
    """
    Teste la suppression du QR 1 (appartient à user 1)
    en étant connecté en tant que user 2.
    """
    response = client.delete("/qrcode/1", headers=auth_headers_user2)
    assert response.status_code == 403 # Forbidden (Non autorisé)

def test_delete_qrcode_ok(client, auth_headers_user1):
    """Teste la suppression réussie par le propriétaire."""
    # Avant : Le QR 1 existe
    response_check1 = client.get("/scan/1", follow_redirects=False)
    assert response_check1.status_code == 307
    
    # Supprimer
    response_delete = client.delete("/qrcode/1", headers=auth_headers_user1)
    assert response_delete.status_code == 200
    
    # Après : Le QR 1 n'existe plus
    response_check2 = client.get("/scan/1", follow_redirects=False)
    assert response_check2.status_code == 404

### 4. Routes de Statistiques (Protégées)

def test_get_stats_unauthorized(client):
    """Teste l'accès aux stats sans token."""
    response = client.get("/qrcode/1/stats")
    assert response.status_code == 401

def test_get_stats_not_owner(client, auth_headers_user2):
    """
    Teste l'accès aux stats du QR 1 (appartient à user 1)
    en étant connecté en tant que user 2.
    """
    response = client.get("/qrcode/1/stats", headers=auth_headers_user2)
    assert response.status_code == 403 # Forbidden

def test_get_stats_not_found(client, auth_headers_user1):
    """Teste l'accès aux stats d'un QR inexistant."""
    response = client.get("/qrcode/999/stats", headers=auth_headers_user1)
    assert response.status_code == 404

def test_get_stats_not_tracked(client, auth_headers_user2):
    """Teste l'accès aux stats d'un QR non-suivi (id=2)."""
    response = client.get("/qrcode/2/stats", headers=auth_headers_user2)
    assert response.status_code == 404 # Non trouvé (car non suivi)

def test_get_stats_ok(client, auth_headers_user1):
    """Teste la récupération réussie des statistiques."""
    response = client.get("/qrcode/1/stats", headers=auth_headers_user1)
    assert response.status_code == 200
    
    data = response.json()
    # Données de pop_db_test.sql pour QR 1
    assert data["id_qrcode"] == 1
    assert data["total_vues"] == 5 # (0 + 5)
    assert data["premiere_vue"] == "2025-10-01"
    assert data["derniere_vue"] == "2025-10-02"
    assert len(data["par_jour"]) == 2
    assert len(data["scans_recents"]) == 2
    assert data["scans_recents"][0]["geo_city"] == "Mountain View" # Le plus récent

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])    