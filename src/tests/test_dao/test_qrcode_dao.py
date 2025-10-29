# tests/test_qrcode_dao.py
from unittest.mock import MagicMock, patch
import pytest
from datetime import datetime

# adapte le chemin suivant si nécessaire
from dao.qrcode_dao import QRCodeDao, QRCodeNotFoundError, UnauthorizedError
from business_object.qr_code import Qrcode


def make_cm(fetchall=None, fetchone=None, rowcount=1):
    """
    Crée un context manager simulé retournant un 'cursor' mock avec fetchall/fetchone/rowcount.
    """
    cursor = MagicMock()
    cursor.fetchall.return_value = fetchall if fetchall is not None else []
    cursor.fetchone.return_value = fetchone
    cursor.rowcount = rowcount
    cm = MagicMock()
    # when "with conn.cursor() as cur:" => cur is cursor
    cm.__enter__.return_value = cursor
    cm.__exit__.return_value = False
    return cm, cursor


def make_qrcode(id_qrcode=1, url="https://ex.com", owner="user-1"):
    return Qrcode(
        id_qrcode=id_qrcode,
        url=url,
        id_proprietaire=owner,
        date_creation=datetime.utcnow(),
        type=True,
        couleur="bleu",
        logo="logo.png",
    )


# -------------------------
# Tests
# -------------------------

@patch("dao.qrcode_dao.DBConnection")
def test_creer_qrc_with_provided_id_returns_true(mock_db_conn):
    """
    Cas : qrcode.id_qrcode fourni -> INSERT avec id ; la DB renvoie une ligne (fetchone)
    """
    fake_conn = MagicMock()
    cm, cur = make_cm(fetchone={"id_qrcode": 10})
    # cursor() returns context manager
    fake_conn.cursor.return_value = cm
    # support "with DBConnection().connection as conn:"
    fake_conn.__enter__.return_value = fake_conn
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    q = make_qrcode(id_qrcode=10)
    res = dao.creer_qrc(q)

    # Vérifie qu'on a tenté un INSERT et que la méthode renvoie True
    assert res is True
    cur.execute.assert_called()
    fake_conn.cursor.assert_called()


@patch("dao.qrcode_dao.DBConnection")
def test_creer_qrc_without_id_returns_true(mock_db_conn):
    """
    Cas : qrcode.id_qrcode None -> INSERT sans id ; la DB renvoie une ligne (fetchone)
    """
    fake_conn = MagicMock()
    cm, cur = make_cm(fetchone={"id_qrcode": 11})
    fake_conn.cursor.return_value = cm
    fake_conn.__enter__.return_value = fake_conn
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    q = make_qrcode(id_qrcode=None)
    res = dao.creer_qrc(q)

    assert res is True
    cur.execute.assert_called()
    # s'assurer que l'insert sans id a été utilisé (on ne peut pas inspecter le SQL facilement ici,
    # mais au moins s'assurer que cur.execute a été invoqué)
    fake_conn.cursor.assert_called()


@patch("dao.qrcode_dao.DBConnection")
def test_trouver_qrc_par_id_user_returns_list_of_qrc(mock_db_conn):
    rows = [
        {
            "id_qrcode": 1,
            "url": "https://a",
            "id_proprietaire": "u1",
            "date_creation": datetime.utcnow(),
            "type": True,
            "couleur": "bleu",
            "logo": "l.png",
        }
    ]
    fake_conn = MagicMock()
    cm, cur = make_cm(fetchall=rows)
    fake_conn.cursor.return_value = cm
    fake_conn.__enter__.return_value = fake_conn
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    result = dao.trouver_qrc_par_id_user("u1")

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Qrcode)
    assert result[0].id_qrcode == 1
    cur.execute.assert_called_once()


@patch("dao.qrcode_dao.DBConnection")
def test_trouver_qrc_par_id_qrc_returns_qrcode_when_found(mock_db_conn):
    row = {
        "id_qrcode": 5,
        "url": "https://found",
        "id_proprietaire": "owner",
        "date_creation": datetime.utcnow(),
        "type": True,
        "couleur": "rouge",
        "logo": "logo.png",
    }
    fake_conn = MagicMock()
    cm, cur = make_cm(fetchone=row)
    fake_conn.cursor.return_value = cm
    fake_conn.__enter__.return_value = fake_conn
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    res = dao.trouver_qrc_par_id_qrc(5)

    assert isinstance(res, Qrcode)
    assert res.id_qrcode == 5
    cur.execute.assert_called_once()


@patch("dao.qrcode_dao.DBConnection")
def test_trouver_qrc_par_id_qrc_returns_none_when_missing(mock_db_conn):
    fake_conn = MagicMock()
    cm, cur = make_cm(fetchone=None)
    fake_conn.cursor.return_value = cm
    fake_conn.__enter__.return_value = fake_conn
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    res = dao.trouver_qrc_par_id_qrc(9999)

    assert res is None
    cur.execute.assert_called_once()


@patch("dao.qrcode_dao.DBConnection")
def test_modifier_qrc_success(mock_db_conn):
    # simulate SELECT owner then UPDATE returning row
    fake_conn = MagicMock()
    # first fetchone for SELECT returns owner row
    # second fetchone for UPDATE RETURNING returns updated row
    cm_select, cur_select = make_cm(fetchone={"id_proprietaire": "u1"})
    cm_update, cur_update = make_cm(fetchone={
        "id_qrcode": 10,
        "url": "https://new",
        "id_proprietaire": "u1",
        "date_creation": datetime.utcnow(),
        "type": True,
        "couleur": "vert",
        "logo": "logo.png",
    })
    # We need conn.cursor() to return a context manager that yields a cursor.
    # Simpler: make a cursor whose fetchone behavior changes between calls.
    cm, cur = make_cm()
    # configure cur.fetchone to return first the select result, then the update result
    cur.fetchone.side_effect = [ {"id_proprietaire": "u1"}, 
                                {
                                    "id_qrcode": 10,
                                    "url": "https://new",
                                    "id_proprietaire": "u1",
                                    "date_creation": datetime.utcnow(),
                                    "type": True,
                                    "couleur": "vert",
                                    "logo": "logo.png",
                                } ]
    fake_conn.cursor.return_value = cm
    fake_conn.__enter__.return_value = fake_conn
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    updated = dao.modifier_qrc(10, "u1", url="https://new")

    assert isinstance(updated, Qrcode)
    assert updated.url == "https://new"
    assert updated.id_proprietaire == "u1"
    assert cur.execute.call_count >= 2  # SELECT then UPDATE


@patch("dao.qrcode_dao.DBConnection")
def test_modifier_qrc_raises_not_found(mock_db_conn):
    fake_conn = MagicMock()
    # SELECT returns None
    cm, cur = make_cm(fetchone=None)
    fake_conn.cursor.return_value = cm
    fake_conn.__enter__.return_value = fake_conn
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    with pytest.raises(QRCodeNotFoundError):
        dao.modifier_qrc(12345, "u1", url="x")


@patch("dao.qrcode_dao.DBConnection")
def test_modifier_qrc_raises_unauthorized(mock_db_conn):
    fake_conn = MagicMock()
    # SELECT returns owner different from caller
    cm, cur = make_cm(fetchone={"id_proprietaire": "other"})
    fake_conn.cursor.return_value = cm
    fake_conn.__enter__.return_value = fake_conn
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    with pytest.raises(UnauthorizedError):
        dao.modifier_qrc(7, "u1", url="x")


@patch("dao.qrcode_dao.DBConnection")
def test_supprimer_returns_true_or_false(mock_db_conn):
    fake_conn = MagicMock()
    # first case: rowcount > 0
    cm1, cur1 = make_cm(rowcount=1)
    fake_conn.cursor.return_value = cm1
    fake_conn.__enter__.return_value = fake_conn
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    q = make_qrcode(id_qrcode=200)
    assert dao.supprimer(q) is True

    # second case: rowcount == 0
    fake_conn2 = MagicMock()
    cm2, cur2 = make_cm(rowcount=0)
    fake_conn2.cursor.return_value = cm2
    fake_conn2.__enter__.return_value = fake_conn2
    mock_db_conn.return_value.connection = fake_conn2

    dao2 = QRCodeDao()
    q2 = make_qrcode(id_qrcode=201)
    assert dao2.supprimer(q2) is False
