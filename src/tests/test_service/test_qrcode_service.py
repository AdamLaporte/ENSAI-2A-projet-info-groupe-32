# tests/test_service/test_qrcode_service.py

from unittest.mock import MagicMock, patch
from datetime import datetime
import pytest
from service.qrcode_service import QRCodeService, QRCodeNotFoundError, UnauthorizedError
from business_object.qr_code import Qrcode


# -------------------------------------------------------------
# TESTS : creation
# -------------------------------------------------------------
def test_creer_qrc_suivi_ok():
    """
    Création d’un QR code suivi (type_qrcode=True).
    - Le DAO crée l'objet.
    - L’image est générée.
    - La méthode retourne un Qrcode enrichi (_image_url, _image_path, _scan_url).
    """
    fake_dao = MagicMock()
    q = Qrcode(id_qrcode=None, url="https://ex.com", id_proprietaire="3")
    q_created = Qrcode(id_qrcode=10, url="https://ex.com", id_proprietaire="3")
    fake_dao.creer_qrc.return_value = q_created

    with patch("service.qrcode_service.generate_and_save_qr_png", return_value="/tmp/f.png") as gen_mock, \
         patch("service.qrcode_service.filepath_to_public_url", return_value="http://x/f.png"):

        service = QRCodeService(fake_dao)
        # SCAN_BASE doit être défini → on simule sa présence
        with patch("service.qrcode_service.SCAN_BASE", "http://scan.me"):
            res = service.creer_qrc(url="https://ex.com", id_proprietaire="3", type_qrcode=True)

    assert isinstance(res, Qrcode)
    assert res.id_qrcode == 10
    assert hasattr(res, "_image_url")
    assert hasattr(res, "_scan_url")
    gen_mock.assert_called_once()


def test_creer_qrc_classique_ok():
    """
    Création d’un QR code classique (type_qrcode=False).
    - Pas d’URL de scan
    - L’image encode directement url
    """
    fake_dao = MagicMock()
    q_created = Qrcode(id_qrcode=7, url="https://ex.com", id_proprietaire=3)
    fake_dao.creer_qrc.return_value = q_created

    with patch("service.qrcode_service.generate_and_save_qr_png", return_value="/tmp/x.png"):
        with patch("service.qrcode_service.filepath_to_public_url", return_value="http://x/x.png"):
            service = QRCodeService(fake_dao)
            res = service.creer_qrc("https://ex.com", 3, type_qrcode=False)

    assert isinstance(res, Qrcode)
    assert res._scan_url is None


def test_creer_qrc_echec():
    """
    Si le DAO retourne None → le service lève RuntimeError.
    """
    fake_dao = MagicMock(return_value=None)
    fake_dao.creer_qrc.return_value = None

    service = QRCodeService(fake_dao)

    with pytest.raises(RuntimeError):
        service.creer_qrc("https://ex.com", "3", True)


# -------------------------------------------------------------
# TESTS : recherche par utilisateur
# -------------------------------------------------------------
def test_trouver_qrc_par_id_user_ok():
    """
    Le service convertit bien id_user en int et appelle le DAO.
    """
    fake_dao = MagicMock()
    expected = [Qrcode(1, "https://ex.com", "3")]
    fake_dao.lister_par_proprietaire.return_value = expected

    service = QRCodeService(fake_dao)
    res = service.trouver_qrc_par_id_user("3")

    assert res == expected
    fake_dao.lister_par_proprietaire.assert_called_once_with(3)


def test_trouver_qrc_par_id_user_bad_input():
    """
    Si id_user n'est pas convertible en int → renvoie [].
    """
    fake_dao = MagicMock()
    service = QRCodeService(fake_dao)

    res = service.trouver_qrc_par_id_user("abc")
    assert res == []


# -------------------------------------------------------------
# TESTS : suppression
# -------------------------------------------------------------
def test_supprimer_qrc_success():
    """
    Suppression autorisée → le DAO est bien appelé.
    """
    fake_dao = MagicMock()
    q = Qrcode(10, "https://ex.com", 3)
    fake_dao.trouver_qrc_par_id_qrc.return_value = q
    fake_dao.supprimer_qrc.return_value = True

    service = QRCodeService(fake_dao)
    assert service.supprimer_qrc(id_qrcode=10, id_user=3) is True


def test_supprimer_qrc_not_found():
    """
    Si le QR n'existe pas → QRCodeNotFoundError.
    """
    fake_dao = MagicMock()
    fake_dao.trouver_qrc_par_id_qrc.return_value = None

    service = QRCodeService(fake_dao)
    with pytest.raises(QRCodeNotFoundError):
        service.supprimer_qrc(99, "3")


def test_supprimer_qrc_unauthorized():
    """
    Si l'utilisateur n'est pas propriétaire → UnauthorizedError.
    """
    fake_dao = MagicMock()
    fake_dao.trouver_qrc_par_id_qrc.return_value = Qrcode(10, "https://ex.com", 1)

    service = QRCodeService(fake_dao)
    with pytest.raises(UnauthorizedError):
        service.supprimer_qrc(10, 4)


# -------------------------------------------------------------
# TESTS : modification
# -------------------------------------------------------------
def test_modifier_qrc_success():
    """Modification autorisée → OK."""
    fake_dao = MagicMock()
    q = Qrcode(id_qrcode=10, url="https://ex.com", id_proprietaire=3)
    fake_dao.trouver_qrc_par_id_qrc.return_value = q
    fake_dao.modifier_qrc.return_value = q

    with patch("service.qrcode_service.SCAN_BASE", "http://scan.me"), \
         patch("service.qrcode_service.generate_and_save_qr_png", return_value="/tmp/f.png"), \
         patch("service.qrcode_service.filepath_to_public_url", return_value="http://x/f.png"):

        service = QRCodeService(fake_dao)
        res = service.modifier_qrc(id_qrcode= 10, id_user=3, url="https://new.com")

    assert res is q



def test_modifier_qrc_not_found():
    """
    Si le QR n'existe pas → QRCodeNotFoundError.
    """

    fake_dao = MagicMock()
    fake_dao.trouver_qrc_par_id_qrc.return_value = None

    service = QRCodeService(fake_dao)
    with pytest.raises(QRCodeNotFoundError):
        service.modifier_qrc(10, 3)


def test_modifier_qrc_unauthorized():
    """
    Si l'utilisateur n'est pas propriétaire → UnauthorizedError.
    """
    fake_dao = MagicMock()
    fake_dao.trouver_qrc_par_id_qrc.return_value = Qrcode(10, "https://ex.com", 3)

    service = QRCodeService(fake_dao)
    with pytest.raises(UnauthorizedError):
        service.modifier_qrc(20, 2, url="x")

    fake_dao.trouver_qrc_par_id_qrc.assert_called_once_with(20)

# --- Tests pour trouver_qrc_par_id ---

def test_trouver_qrc_par_id_ok():
    """
    Teste la recherche simple par ID via le service.
    """
    fake_dao = MagicMock()
    expected_qr = Qrcode(id_qrcode=1, url="http://test.com", id_proprietaire=1)
    fake_dao.trouver_qrc_par_id_qrc.return_value = expected_qr
    
    service = QRCodeService(fake_dao)
    result = service.trouver_qrc_par_id(1)
    
    assert result == expected_qr
    fake_dao.trouver_qrc_par_id_qrc.assert_called_once_with(1)

def test_trouver_qrc_par_id_non_trouve():
    """
    Teste la recherche simple par ID (non trouvé) via le service.
    """
    fake_dao = MagicMock()
    fake_dao.trouver_qrc_par_id_qrc.return_value = None
    
    service = QRCodeService(fake_dao)
    result = service.trouver_qrc_par_id(999)
    
    assert result is None
    fake_dao.trouver_qrc_par_id_qrc.assert_called_once_with(999)

# --- Test pour la logique de création (SCAN_BASE manquant) ---

def test_creer_qrc_suivi_echec_env_var():
    """
    Teste que la création d'un QR suivi (type_qrcode=True) échoue
    si SCAN_BASE n'est pas défini dans l'environnement.
   
    """
    fake_dao = MagicMock()
    q_created = Qrcode(id_qrcode=10, url="https://ex.com", id_proprietaire="3")
    fake_dao.creer_qrc.return_value = q_created

    service = QRCodeService(fake_dao)
    
    # Simule l'absence de la variable d'environnement
    with patch("service.qrcode_service.SCAN_BASE", None):
        with pytest.raises(RuntimeError, match="SCAN_BASE_URL n'est pas configuré"):
            service.creer_qrc(url="https://ex.com", id_proprietaire="3", type_qrcode=True)

# --- Tests pour la logique de re-génération d'image dans modifier_qrc ---

@patch("service.qrcode_service.generate_and_save_qr_png")
def test_modifier_qrc_statique_change_url_regenere(mock_gen_png):
    """
    Modifier l'URL d'un QR statique (type=False) DOIT re-générer l'image.
   
    """
    fake_dao = MagicMock()
    qr_statique = Qrcode(10, "https://old.com", 3, type_qrcode=False)
    fake_dao.trouver_qrc_par_id_qrc.return_value = qr_statique
    fake_dao.modifier_qrc.return_value = qr_statique # Retourne l'objet modifié

    service = QRCodeService(fake_dao)
    service.modifier_qrc(id_qrcode=10, id_user=3, url="https://new.com")
    
    mock_gen_png.assert_called_once() # L'image a été re-générée

@patch("service.qrcode_service.generate_and_save_qr_png")
def test_modifier_qrc_dynamique_change_url_ne_regenere_pas(mock_gen_png):
    """
    Modifier l'URL d'un QR dynamique (type=True) NE DOIT PAS re-générer l'image.
    (Car l'image contient l'URL de scan, qui ne change pas).
    """
    fake_dao = MagicMock()
    qr_dynamique = Qrcode(10, "https://old.com", 3, type_qrcode=True)
    fake_dao.trouver_qrc_par_id_qrc.return_value = qr_dynamique
    fake_dao.modifier_qrc.return_value = qr_dynamique

    service = QRCodeService(fake_dao)
    # Simule SCAN_BASE pour que le service ne plante pas
    with patch("service.qrcode_service.SCAN_BASE", "http://scan.me"):
        service.modifier_qrc(id_qrcode=10, id_user=3, url="https://new.com")
    
    mock_gen_png.assert_not_called() # L'image n'a PAS été re-générée

@patch("service.qrcode_service.generate_and_save_qr_png")
def test_modifier_qrc_change_couleur_regenere(mock_gen_png):
    """
    Modifier la COULEUR d'un QR (statique ou dynamique) DOIT re-générer l'image.
   
    """
    fake_dao = MagicMock()
    qr_dynamique = Qrcode(10, "https://url.com", 3, type_qrcode=True, couleur="black")
    fake_dao.trouver_qrc_par_id_qrc.return_value = qr_dynamique
    fake_dao.modifier_qrc.return_value = qr_dynamique

    service = QRCodeService(fake_dao)
    with patch("service.qrcode_service.SCAN_BASE", "http://scan.me"):
        service.modifier_qrc(id_qrcode=10, id_user=3, couleur="blue")
    
    mock_gen_png.assert_called_once() # L'image a été re-générée

@patch("service.qrcode_service.generate_and_save_qr_png")
def test_modifier_qrc_passe_statique_a_dynamique_regenere(mock_gen_png):
    """
    Changer un QR de statique (False) à dynamique (True) DOIT re-générer l'image.
    (Car l'image doit maintenant contenir l'URL de scan).
   
    """
    fake_dao = MagicMock()
    qr_statique = Qrcode(10, "https://url.com", 3, type_qrcode=False)
    fake_dao.trouver_qrc_par_id_qrc.return_value = qr_statique
    fake_dao.modifier_qrc.return_value = qr_statique

    service = QRCodeService(fake_dao)
    with patch("service.qrcode_service.SCAN_BASE", "http://scan.me"):
        service.modifier_qrc(id_qrcode=10, id_user=3, type_qrcode=True)
    
    mock_gen_png.assert_called_once() # L'image a été re-générée

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
