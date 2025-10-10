# tests/test_qrcode_dao.py
from unittest.mock import MagicMock, patch
import pytest

import dao.qrcode_dao as dao_module
from dao.qrcode_dao import QRCodeDao, QRCodeNotFoundError, UnauthorizedError

def make_cm(fetchall=None, fetchone=None, rowcount=1):
    """
    Crée un context manager simulé retournant un 'cursor' mock
    avec fetchall, fetchone et rowcount configurés.
    """
    cursor = MagicMock()
    cursor.fetchall.return_value = fetchall if fetchall is not None else []
    cursor.fetchone.return_value = fetchone
    cursor.rowcount = rowcount
    cm = MagicMock()
    cm.__enter__.return_value = cursor
    cm.__exit__.return_value = False
    return cm, cursor


# Une petite classe Qrcode factice pour remplacer la vraie dans le module DAO lors des tests
class FakeQrcode:
    def __init__(self, id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo):
        self.id_qrcode = id_qrcode
        self.url = url
        self.id_proprietaire = id_proprietaire
        self.date_creation = date_creation
        self.type = type
        self.couleur = couleur
        self.logo = logo

    def get_id(self):
        return self.id_qrcode

    def get_url(self):
        return self.url


@patch('dao.db_connexion.DBConnection')
def test_creer_qrc_commits_and_returns_true(mock_db_conn):
    # préparation de la connexion/cursor simulés
    fake_conn = MagicMock()
    cm, cur = make_cm()
    fake_conn.cursor.return_value = cm
    mock_db_conn.return_value.connection = fake_conn

    # qrcode factice attendu par créer_qrc (on respecte l'interface du DAO)
    class SimpleQr:
        def __init__(self):
            self._id = 'qr-1'
            self._url = 'https://ex.com'
            # accès aux attributs "privés" comme dans ton DAO
            self._Qrcode__id_proprietaire = 'user-1'
            self._Qrcode__date_creation = '2025-01-01'
            self._Qrcode__type = True
            self._Qrcode__couleur = 'bleu'
            self._Qrcode__logo = 'logo.png'

        def get_id(self):
            return self._id

        def get_url(self):
            return self._url

    dao = QRCodeDao()
    result = dao.créer_qrc(SimpleQr())

    # assertions
    cur.execute.assert_called()          # on a bien appelé execute
    fake_conn.commit.assert_called_once()  # commit bien fait
    assert result is True


@patch('dao.db_connexion.DBConnection')
def test_trouver_par_id_returns_list_of_qrc(mock_db_conn):
    fake_conn = MagicMock()
    rows = [
        {
            "id_qrcode": "qr-1",
            "url": "https://ex.com",
            "id_proprietaire": "user-1",
            "date_creation": "2025-01-01",
            "type": True,
            "couleur": "bleu",
            "logo": "logo.png",
        }
    ]
    cm, cur = make_cm(fetchall=rows)
    fake_conn.cursor.return_value = cm
    mock_db_conn.return_value.connection = fake_conn

    # Patch de la classe Qrcode utilisée dans le module DAO pour ne pas dépendre de l'implémentation réelle
    with patch.object(dao_module, 'Qrcode', FakeQrcode):
        dao = QRCodeDao()
        result = dao.trouver_par_id("user-1")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id_qrcode == "qr-1"
    assert result[0].url == "https://ex.com"


@patch('dao.db_connexion.DBConnection')
def test_modifier_qrc_updates_and_returns_qrcode(mock_db_conn):
    fake_conn = MagicMock()
    # Simule la lecture préalable (fetchone renvoie la ligne existante)
    row = {
        "id_proprietaire": "user-1",
        "url": "https://old.example",
        "date_creation": "2025-01-01",
        "type": True,
        "couleur": "bleu",
        "logo": "logo.png",
    }
    cm, cur = make_cm(fetchone=row)
    fake_conn.cursor.return_value = cm
    mock_db_conn.return_value.connection = fake_conn

    with patch.object(dao_module, 'Qrcode', FakeQrcode):
        dao = QRCodeDao()
        updated = dao.modifier_qrc(
            id_qrcode=123,
            id_user="user-1",
            url="https://new.example",
            type_=None,
            couleur=None,
            logo=None,
        )

    # l'UPDATE a été appelé puis commit
    # on vérifie qu'une execute a eu lieu pour l'update (la deuxième execute)
    assert cur.execute.call_count >= 2
    fake_conn.commit.assert_called_once()

    # vérifie que l'objet retourné contient la nouvelle URL et l'ancien propriétaire
    assert isinstance(updated, FakeQrcode)
    assert updated.url == "https://new.example"
    assert updated.id_proprietaire == "user-1"


@patch('dao.db_connexion.DBConnection')
def test_modifier_qrc_raises_not_found(mock_db_conn):
    fake_conn = MagicMock()
    cm, cur = make_cm(fetchone=None)  # pas de ligne trouvée
    fake_conn.cursor.return_value = cm
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    with pytest.raises(QRCodeNotFoundError):
        dao.modifier_qrc(id_qrcode=999, id_user="user-1")


@patch('dao.db_connexion.DBConnection')
def test_modifier_qrc_raises_unauthorized(mock_db_conn):
    fake_conn = MagicMock()
    row = {
        "id_proprietaire": "someone_else",
        "url": "https://old.example",
        "date_creation": "2025-01-01",
        "type": True,
        "couleur": "bleu",
        "logo": "logo.png",
    }
    cm, cur = make_cm(fetchone=row)
    fake_conn.cursor.return_value = cm
    mock_db_conn.return_value.connection = fake_conn

    dao = QRCodeDao()
    with pytest.raises(UnauthorizedError):
        dao.modifier_qrc(id_qrcode=123, id_user="user-1", url="https://new.example")


@patch('dao.db_connexion.DBConnection')
def test_supprimer_returns_true_or_false(mock_db_conn):
    fake_conn = MagicMock()
    # cas deleted = True
    cm1, cur1 = make_cm(rowcount=1)
    fake_conn.cursor.return_value = cm1
    mock_db_conn.return_value.connection = fake_conn
    dao = QRCodeDao()

    class SimpleQr:
        def __init__(self):
            self._id = 'qr-1'
        def get_id(self):
            return self._id

    assert dao.supprimer(SimpleQr()) is True
    fake_conn.commit.assert_called()

    # cas deleted = False (rowcount = 0)
    fake_conn2 = MagicMock()
    cm2, cur2 = make_cm(rowcount=0)
    fake_conn2.cursor.return_value = cm2
    mock_db_conn.return_value.connection = fake_conn2
    dao2 = QRCodeDao()
    assert dao2.supprimer(SimpleQr()) is False
