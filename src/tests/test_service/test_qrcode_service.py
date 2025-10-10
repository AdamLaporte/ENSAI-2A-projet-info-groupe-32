from unittest.mock import MagicMock, patch
import pytest

from service.qrcode_service import QRCodeService, QRCodeNotFoundError, UnauthorizedError

# On crée une classe Qrcode factice pour les besoins du test
class FakeQrcode:
    def __init__(self, id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo):
        self._Qrcode__id_proprietaire = id_proprietaire
        self._Qrcode__id_qrcode = id_qrcode
        self._Qrcode__url = url
        self._Qrcode__date_creation = date_creation
        self._Qrcode__type = type
        self._Qrcode__couleur = couleur
        self._Qrcode__logo = logo

    def get_id(self):
        return self._Qrcode__id_qrcode

    def get_url(self):
        return self._Qrcode__url


@pytest.fixture
def fake_dao():
    """Crée un DAO simulé (mock) pour isoler la logique métier."""
    return MagicMock()


@patch("service.qrcode_service.Qrcode", FakeQrcode)
def test_creer_qrc_appelle_dao_et_retourne_qrcode(fake_dao):
    service = QRCodeService(fake_dao)

    q = service.creer_qrc(
        url="https://test.com",
        type_=True,
        couleur="bleu",
        logo="logo.png",
        id_proprietaire="user-1",
        id_qrcode=123,
    )

    # ✅ Le DAO doit avoir été appelé pour insérer le QRCode
    fake_dao.créer_qrc.assert_called_once()
    assert isinstance(q, FakeQrcode)
    assert q.get_url() == "https://test.com"
    assert q._Qrcode__id_proprietaire == "user-1"


def test_trouver_qrc_par_id_user_retourne_liste(fake_dao):
    fake_dao.trouver_par_id.return_value = [FakeQrcode(1, "url", "u1", "2025", True, "red", "logo.png")]

    service = QRCodeService(fake_dao)
    result = service.trouver_qrc_par_id_user("u1")

    fake_dao.trouver_par_id.assert_called_once_with("u1")
    assert isinstance(result, list)
    assert isinstance(result[0], FakeQrcode)


def test_supprimer_qrc_appelle_dao(fake_dao):
    fake_dao.supprimer.return_value = True
    service = QRCodeService(fake_dao)

    q = FakeQrcode(1, "url", "u1", "2025", True, "blue", "logo.png")
    result = service.supprimer_qrc(q)

    fake_dao.supprimer.assert_called_once_with(q)
    assert result is True


def test_verifier_proprietaire_vrai_ou_faux(fake_dao):
    service = QRCodeService(fake_dao)
    q = FakeQrcode(1, "url", "owner1", "2025", True, "blue", "logo.png")

    assert service.verifier_proprietaire(q, "owner1") is True
    assert service.verifier_proprietaire(q, "someone_else") is False


def test_modifier_qrc_appelle_dao_et_retourne_objet(fake_dao):
    q_modifie = FakeQrcode(1, "newurl", "user-1", "2025", True, "green", "logo.png")
    fake_dao.modifier_qrc.return_value = q_modifie

    service = QRCodeService(fake_dao)
    result = service.modifier_qrc(
        id_qrcode=1,
        id_user="user-1",
        url="newurl",
        type_=True,
        couleur="green",
        logo="logo.png",
    )

    # ✅ Le DAO doit avoir été appelé avec les bons paramètres
    fake_dao.modifier_qrc.assert_called_once_with(
        id_qrcode=1,
        id_user="user-1",
        url="newurl",
        type_=True,
        couleur="green",
        logo="logo.png",
    )
    assert result is q_modifie


def test_modifier_qrc_leve_exceptions(fake_dao):
    """Vérifie que les exceptions du DAO sont bien relayées par le service."""
    service = QRCodeService(fake_dao)

    # Cas 1 : QRCodeNotFoundError
    fake_dao.modifier_qrc.side_effect = QRCodeNotFoundError("Introuvable")
    with pytest.raises(QRCodeNotFoundError):
        service.modifier_qrc(1, "user")

    # Cas 2 : UnauthorizedError
    fake_dao.modifier_qrc.side_effect = UnauthorizedError("Pas autorisé")
    with pytest.raises(UnauthorizedError):
        service.modifier_qrc(1, "user")
