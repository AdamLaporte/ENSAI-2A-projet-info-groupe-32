# tests/test_qrcode_service.py
from unittest.mock import MagicMock
import pytest
from datetime import datetime


from service.qrcode_service import (
    QRCodeService,
    QRCodeNotFoundError,
    UnauthorizedError,
)
from business_object.qr_code import Qrcode


# --- Fixtures utiles -------------------------------------------------------
@pytest.fixture
def fake_dao():
    """Donne un DAO factice (mock) réinitialisé pour chaque test."""
    return MagicMock()


def make_qrcode(id_qrcode=1, url="https://ex.com", owner="user-1"):
    """Crée une instance Qrcode simple pour les tests."""
    return Qrcode(
        id_qrcode=id_qrcode,
        url=url,
        id_proprietaire=owner,
        date_creation=datetime.utcnow(),
        type=True,
        couleur="bleu",
        logo="logo.png",
    )


# --- Tests ---------------------------------------------------------------
def test_creer_qrc_calls_dao_and_returns_created(fake_dao):
    service = QRCodeService(fake_dao)

    # préparer le Qrcode que le DAO renverra (généré par la BDD)
    created = make_qrcode(id_qrcode=42, url="https://created.example", owner="u1")
    fake_dao.creer_qrc.return_value = created

    result = service.creer_qrc(url="https://created.example", id_proprietaire="u1")

    # vérifier que le DAO a été appelé exactement une fois
    assert fake_dao.creer_qrc.call_count == 1

    # vérifier que le service retourne bien l'objet renvoyé par le DAO
    assert result is created

    # inspecter l'argument passé au DAO : c'est un Qrcode dont id_qrcode était None
    passed_qrcode = fake_dao.creer_qrc.call_args[0][0]
    assert isinstance(passed_qrcode, Qrcode)
    assert passed_qrcode.url == "https://created.example"
    # id_qrcode doit être None avant insertion (la DB génère l'id)
    assert passed_qrcode.id_qrcode is None


def test_trouver_qrc_par_id_user_forwards_call(fake_dao):
    service = QRCodeService(fake_dao)
    qlist = [make_qrcode(1, owner="u1"), make_qrcode(2, owner="u1")]
    fake_dao.trouver_qrc_par_id_user.return_value = qlist

    res = service.trouver_qrc_par_id_user("u1")

    fake_dao.trouver_qrc_par_id_user.assert_called_once_with("u1")
    assert res == qlist


def test_supprimer_qrc_success_when_owner_matches(fake_dao):
    service = QRCodeService(fake_dao)
    qr = make_qrcode(id_qrcode=123, owner="owner1")

    # DAO doit retourner le QR existant par son id (trouver_qrc_par_id_qrc)
    fake_dao.trouver_qrc_par_id_qrc.return_value = qr
    fake_dao.supprimer_qrc.return_value = True

    res = service.supprimer_qrc(123, "owner1")

    fake_dao.trouver_qrc_par_id_qrc.assert_called_once_with(123)
    fake_dao.supprimer_qrc.assert_called_once_with(qr)
    assert res is True


def test_supprimer_qrc_raises_not_found_when_missing(fake_dao):
    service = QRCodeService(fake_dao)
    fake_dao.trouver_qrc_par_id_qrc.return_value = None

    with pytest.raises(QRCodeNotFoundError):
        service.supprimer_qrc(999, "owner1")

    fake_dao.trouver_qrc_par_id_qrc.assert_called_once_with(999)


def test_supprimer_qrc_raises_unauthorized_when_owner_mismatch(fake_dao):
    service = QRCodeService(fake_dao)
    qr = make_qrcode(id_qrcode=55, owner="someone_else")
    fake_dao.trouver_qrc_par_id_qrc.return_value = qr

    with pytest.raises(UnauthorizedError):
        service.supprimer_qrc(55, "owner1")

    fake_dao.trouver_qrc_par_id_qrc.assert_called_once_with(55)


def test_modifier_qrc_success_calls_dao_and_returns_updated(fake_dao):
    service = QRCodeService(fake_dao)
    existing = make_qrcode(id_qrcode=10, owner="u1")
    updated = make_qrcode(id_qrcode=10, url="https://new.example", owner="u1")

    # DAO trouve l'objet par id
    fake_dao.trouver_qrc_par_id.return_value = existing
    # DAO.modifier_qrc renvoie l'objet mis à jour
    fake_dao.modifier_qrc.return_value = updated

    res = service.modifier_qrc(
        id_qrcode=10,
        id_user="u1",
        url="https://new.example",
        type_=None,
        couleur=None,
        logo=None,
    )

    fake_dao.trouver_qrc_par_id.assert_called_once_with(10)
    fake_dao.modifier_qrc.assert_called_once_with(
        id_qrcode=10,
        url="https://new.example",
        type_=None,
        couleur=None,
        logo=None,
    )
    assert res is updated


def test_modifier_qrc_raises_not_found_when_missing(fake_dao):
    service = QRCodeService(fake_dao)
    fake_dao.trouver_qrc_par_id.return_value = None

    with pytest.raises(QRCodeNotFoundError):
        service.modifier_qrc(1, "u1", url="x")

    fake_dao.trouver_qrc_par_id.assert_called_once_with(1)


def test_modifier_qrc_raises_unauthorized_when_owner_mismatch(fake_dao):
    service = QRCodeService(fake_dao)
    existing = make_qrcode(id_qrcode=20, owner="other")
    fake_dao.trouver_qrc_par_id.return_value = existing

    with pytest.raises(UnauthorizedError):
        service.modifier_qrc(20, "u1", url="x")

    fake_dao.trouver_qrc_par_id.assert_called_once_with(20)
