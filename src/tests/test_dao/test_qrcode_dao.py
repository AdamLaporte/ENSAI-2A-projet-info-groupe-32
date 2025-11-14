import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


from utils.reset_database import ResetDatabase
from dao.qrcode_dao import QRCodeDao, QRCodeNotFoundError, UnauthorizedError
from business_object.qr_code import Qrcode


@pytest.fixture(scope="function", autouse=True)
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
    """
    Vérifie que la création d’un QR code sans identifiant explicite :
    - insère correctement le QR code en base,
    - renvoie un objet Qrcode valide,
    - assigne un id_qrcode auto-généré,
    - et définit une date_creation.
    """
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
    """
    Vérifie que la recherche d’un QR code par son id :
    - renvoie l’objet Qrcode associé lorsque l’id existe en base.
    """
    dao = QRCodeDao()

    # Créer d'abord un QR pour être sûr qu'il existe
    created = dao.creer_qrc(Qrcode(id_qrcode=None, url="https://test", id_proprietaire=3))
    found = dao.trouver_qrc_par_id_qrc(created.id_qrcode)

    assert isinstance(found, Qrcode)
    assert found.id_qrcode == created.id_qrcode


def test_trouver_qrc_par_id_qrc_returns_none_when_missing():
    """
    Vérifie que la recherche d’un QR code inexistant renvoie None.
    Aucun QR code ne doit être retourné pour un id qui n’est pas en base.
    """
    dao = QRCodeDao()
    res = dao.trouver_qrc_par_id_qrc(99999999)
    assert res is None


def test_modifier_qrc_success():
    """
    Vérifie que la modification d’un QR code :
    - fonctionne lorsque l’utilisateur propriétaire correspond,
    - met bien à jour les champs modifiés,
    - renvoie un objet Qrcode avec les nouvelles valeurs.
    """
    dao = QRCodeDao()

    q = dao.creer_qrc(Qrcode(id_qrcode=None, url="https://old", id_proprietaire=3))
    updated = dao.modifier_qrc(q.id_qrcode, 3, url="https://new")

    assert isinstance(updated, Qrcode)
    assert updated.url == "https://new"


def test_modifier_qrc_raises_not_found():
    """
    Vérifie que tenter de modifier un QR code avec un ID inexistant
    déclenche l’exception QRCodeNotFoundError.
    """
    dao = QRCodeDao()
    with pytest.raises(QRCodeNotFoundError):
        dao.modifier_qrc(123456789, "u1", url="x")


def test_modifier_qrc_raises_unauthorized():
    """
    Vérifie que la modification d’un QR code par un utilisateur qui n’en est pas
    le propriétaire déclenche UnauthorizedError.
    """
    dao = QRCodeDao()

    q = dao.creer_qrc(Qrcode(id_qrcode=None, url="https://secure", id_proprietaire=3))
    with pytest.raises(UnauthorizedError):
        dao.modifier_qrc(id_qrcode=q.id_qrcode, url="x", id_user=4)


def test_supprimer_returns_true_or_false():
    """
    Vérifie que la suppression d’un QR code :
    - renvoie True si la ligne est réellement supprimée,
    - renvoie False si aucun QR code ne correspond à l’id fourni.
    """
    dao = QRCodeDao()

    # cas supprimé
    q1 = dao.creer_qrc(Qrcode(id_qrcode=None, url="https://todel", id_proprietaire=3))
    assert dao.supprimer_qrc(q1.id_qrcode)

    # cas échec (id inexistant)
    assert dao.supprimer_qrc(999999) is False

def test_lister_par_proprietaire_ok():
    """
    Vérifie que la liste des QR codes est correcte pour un utilisateur.
    La BDD de test (pop_db_test.sql) crée l'utilisateur 'test_u3' (id 3)
    et lui assigne un QR code.
   
    """
    dao = QRCodeDao()
    id_user_3 = 3  # Basé sur pop_db_test.sql
    
    resultats = dao.lister_par_proprietaire(id_user_3)
    
    assert isinstance(resultats, list)
    assert len(resultats) == 1
    assert isinstance(resultats[0], Qrcode)
    assert resultats[0].url == "https://t.local/u3/c"

def test_lister_par_proprietaire_aucun_resultat():
    """
    Vérifie qu'une liste vide est retournée pour un utilisateur
    qui n'a pas de QR codes (ou un ID inexistant).
    """
    dao = QRCodeDao()
    id_user_inexistant = 99999
    
    resultats = dao.lister_par_proprietaire(id_user_inexistant)
    
    assert isinstance(resultats, list)
    assert len(resultats) == 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
