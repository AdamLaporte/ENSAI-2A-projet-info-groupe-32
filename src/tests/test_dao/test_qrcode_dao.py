# tests/test_dao/test_qrcode_dao.py
import pytest
from unittest.mock import MagicMock, patch
from business_object.qr_code import Qrcode
from dao.qrcode_dao import QRCodeDao, QRCodeNotFoundError, UnauthorizedError

# Fixture QRCode exemple
@pytest.fixture
def sample_qrcode():
    return Qrcode(
        id_qrcode=1,
        url="https://example.com",
        id_proprietaire="user123",
        date_creation="2025-10-23",
        type=True,
        couleur="red",
        logo="logo.png"
    )

# ==========================
# Tests avec DBConnection mockée
# ==========================

def test_creer_qrc(sample_qrcode):
    with patch("dao.qrcode_dao.DBConnection") as mock_db_cls:
        mock_db = mock_db_cls.return_value
        mock_conn = mock_db.connection.__enter__.return_value
        mock_cursor = mock_conn.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = {"id_qrcode": 1}

        dao = QRCodeDao()
        res = dao.creer_qrc(sample_qrcode)
        assert res is True
        mock_cursor.execute.assert_called()

def test_trouver_qrc_par_id_user(sample_qrcode):
    with patch("dao.qrcode_dao.DBConnection") as mock_db_cls:
        mock_db = mock_db_cls.return_value
        mock_conn = mock_db.connection.__enter__.return_value
        mock_cursor = mock_conn.cursor.__enter__.return_value
        mock_cursor.fetchall.return_value = [
            {
                "id_qrcode": sample_qrcode.id_qrcode,
                "url": sample_qrcode.url,
                "id_proprietaire": sample_qrcode.id_proprietaire,
                "date_creation": sample_qrcode.date_creation,
                "type": sample_qrcode.type,
                "couleur": sample_qrcode.couleur,
                "logo": sample_qrcode.logo,
            }
        ]

        dao = QRCodeDao()
        res = dao.trouver_qrc_par_id_user("user123")
        assert len(res) == 1
        assert res[0].id_qrcode == sample_qrcode.id_qrcode

def test_trouver_qrc_par_id_qrc(sample_qrcode):
    with patch("dao.qrcode_dao.DBConnection") as mock_db_cls:
        mock_db = mock_db_cls.return_value
        mock_conn = mock_db.connection.__enter__.return_value
        mock_cursor = mock_conn.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = {
            "id_qrcode": sample_qrcode.id_qrcode,
            "url": sample_qrcode.url,
            "id_proprietaire": sample_qrcode.id_proprietaire,
            "date_creation": sample_qrcode.date_creation,
            "type": sample_qrcode.type,
            "couleur": sample_qrcode.couleur,
            "logo": sample_qrcode.logo,
        }

        dao = QRCodeDao()
        res = dao.trouver_qrc_par_id_qrc(1)
        assert res.id_qrcode == 1

def test_modifier_qrc_success(sample_qrcode):
    with patch("dao.qrcode_dao.DBConnection") as mock_db_cls:
        mock_db = mock_db_cls.return_value
        mock_conn = mock_db.connection.__enter__.return_value
        mock_cursor = mock_conn.cursor.__enter__.return_value
        # fetchone pour check existence puis update returning
        mock_cursor.fetchone.side_effect = [
            {"id_proprietaire": sample_qrcode.id_proprietaire},
            {
                "id_qrcode": sample_qrcode.id_qrcode,
                "url": "https://new-url.com",
                "id_proprietaire": sample_qrcode.id_proprietaire,
                "date_creation": sample_qrcode.date_creation,
                "type": sample_qrcode.type,
                "couleur": sample_qrcode.couleur,
                "logo": sample_qrcode.logo,
            }
        ]

        dao = QRCodeDao()
        res = dao.modifier_qrc(
            id_qrcode=1,
            id_user="user123",
            url="https://new-url.com"
        )
        assert res.url == "https://new-url.com"

def test_modifier_qrc_not_found(sample_qrcode):
    with patch("dao.qrcode_dao.DBConnection") as mock_db_cls:
        mock_db = mock_db_cls.return_value
        mock_conn = mock_db.connection.__enter__.return_value
        mock_cursor = mock_conn.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        dao = QRCodeDao()
        with pytest.raises(QRCodeNotFoundError):
            dao.modifier_qrc(id_qrcode=99, id_user="user123")

def test_modifier_qrc_unauthorized(sample_qrcode):
    with patch("dao.qrcode_dao.DBConnection") as mock_db_cls:
        mock_db = mock_db_cls.return_value
        mock_conn = mock_db.connection.__enter__.return_value
        mock_cursor = mock_conn.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = {"id_proprietaire": "other_user"}

        dao = QRCodeDao()
        with pytest.raises(UnauthorizedError):
            dao.modifier_qrc(id_qrcode=1, id_user="user123")

def test_supprimer(sample_qrcode):
    with patch("dao.qrcode_dao.DBConnection") as mock_db_cls:
        mock_db = mock_db_cls.return_value
        mock_conn = mock_db.connection.__enter__.return_value
        mock_cursor = mock_conn.cursor.__enter__.return_value
        mock_cursor.rowcount = 1

        dao = QRCodeDao()
        res = dao.supprimer(sample_qrcode)
        assert res is True
