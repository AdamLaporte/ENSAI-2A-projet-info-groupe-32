
import os
from unittest.mock import MagicMock, patch
import pytest
from datetime import datetime


from utils.reset_database import ResetDatabase
from dao.qrcode_dao import QRCodeDao, QRCodeNotFoundError, UnauthorizedError
from business_object.qr_code import Qrcode


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Initialise une base dédiée aux tests d'intégration.
    On force le schéma projet_test_dao pour éviter d'utiliser les vraies données.
    """
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("POSTGRES_SCHEMA", "projet_test_dao")
        ResetDatabase().lancer(test_dao=True)
        yield


def test_creer_qrc_without_id_returns_qrcode():
    dao = QRCodeDao()
    q = Qrcode(
        id_qrcode=None, 
        url="https://ex.com",
        id_proprietaire=3,
        type_qrcode=True,
        couleur="bleu",
        logo=None,
    )

    res = dao.creer_qrc(q)

    assert isinstance(res, Qrcode)
    assert res.id_qrcode is not None  # auto-généré en DB
    assert isinstance(res.date_creation, datetime)


def test_trouver_qrc_par_id_qrc_returns_qrcode_when_found():
    dao = QRCodeDao()

    # Créer d'abord un QR pour être sûr qu'il existe
    created = dao.creer_qrc(Qrcode(id_qrcode=None, url= "https://test", id_proprietaire= 3))
    found = dao.trouver_qrc_par_id_qrc(created.id_qrcode)

    assert isinstance(found, Qrcode)
    assert found.id_qrcode == created.id_qrcode


def test_trouver_qrc_par_id_qrc_returns_none_when_missing():
    dao = QRCodeDao()
    res = dao.trouver_qrc_par_id_qrc(99999999)
    assert res is None


def test_modifier_qrc_success():
    dao = QRCodeDao()

    q = dao.creer_qrc(Qrcode(id_qrcode=None, url= "https://old", id_proprietaire=3))
    updated = dao.modifier_qrc(q.id_qrcode, 3, url="https://new")

    assert isinstance(updated, Qrcode)
    assert updated.url == "https://new"


def test_modifier_qrc_raises_not_found():
    dao = QRCodeDao()
    with pytest.raises(QRCodeNotFoundError):
        dao.modifier_qrc(123456789, "u1", url="x")


def test_modifier_qrc_raises_unauthorized():
    dao = QRCodeDao()

    q = dao.creer_qrc(Qrcode(id_qrcode=None,url= "https://secure", id_proprietaire=3))
    with pytest.raises(UnauthorizedError):
        dao.modifier_qrc(id_qrcode=q.id_qrcode, url="x", id_user=4)


def test_supprimer_returns_true_or_false():
    dao = QRCodeDao()

    # cas supprimé
    q1 = dao.creer_qrc(Qrcode(id_qrcode=None, url="https://todel",id_proprietaire= 3))
    assert dao.supprimer_qrc(q1.id_qrcode) 

    # cas échec
    assert dao.supprimer_qrc(999999) is False
