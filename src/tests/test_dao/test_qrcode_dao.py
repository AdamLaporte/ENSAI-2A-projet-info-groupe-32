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
    Teste la création d’un QR code sans identifiant fourni.

    Paramètres
    ----------
    Aucun paramètre externe. Un objet Qrcode est créé dans le test avec
    id_qrcode=None.

    Retour
    ------
    None
        Le test vérifie :
        - que creer_qrc insère correctement le QR code,
        - que l’objet retourné est un Qrcode valide,
        - que l’id_qrcode auto-généré est bien défini,
        - que la date_creation est renseignée.

    Notes
    -----
    Le test utilise un id_proprietaire existant en base de tests (id=3).
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
    assert res.id_qrcode is not None
    assert isinstance(res.date_creation, datetime)


def test_trouver_qrc_par_id_qrc_returns_qrcode_when_found():
    """
    Teste la récupération d’un QR code par son identifiant.

    Paramètres
    ----------
    Aucun paramètre externe. Le test commence par créer un QR code
    pour garantir son existence.

    Retour
    ------
    None
        Le test confirme que :
        - trouver_qrc_par_id_qrc retourne bien un objet Qrcode,
        - l’identifiant correspond à celui créé.

    Notes
    -----
    Le test crée un QR code afin d'éviter toute dépendance à l'état initial de la base.
    """
    dao = QRCodeDao()

    created = dao.creer_qrc(Qrcode(id_qrcode=None, url="https://test", id_proprietaire=3))
    found = dao.trouver_qrc_par_id_qrc(created.id_qrcode)

    assert isinstance(found, Qrcode)
    assert found.id_qrcode == created.id_qrcode


def test_trouver_qrc_par_id_qrc_returns_none_when_missing():
    """
    Teste la recherche d’un QR code inexistant.

    Paramètres
    ----------
    Aucun paramètre externe. Un identifiant très élevé (99999999) est utilisé.

    Retour
    ------
    None
        Le test vérifie que :
        - la fonction retourne None pour un id non présent en base.

    Notes
    -----
    Aucune exception ne doit être levée pour ce cas.
    """
    dao = QRCodeDao()
    res = dao.trouver_qrc_par_id_qrc(99999999)
    assert res is None


def test_modifier_qrc_success():
    """
    Teste la modification réussie d’un QR code existant.

    Paramètres
    ----------
    Aucun paramètre externe. Le test crée un QR code avant modification.

    Retour
    ------
    None
        Le test valide que :
        - la modification renvoie un Qrcode,
        - les champs modifiés (url) sont correctement mis à jour.

    Notes
    -----
    L’utilisateur propriétaire (id_user=3) est utilisé pour autoriser la modification.
    """
    dao = QRCodeDao()

    q = dao.creer_qrc(Qrcode(id_qrcode=None, url="https://old", id_proprietaire=3))
    updated = dao.modifier_qrc(q.id_qrcode, 3, url="https://new")

    assert isinstance(updated, Qrcode)
    assert updated.url == "https://new"


def test_modifier_qrc_raises_not_found():
    """
    Teste le cas où la modification d’un QR code utilise un id inexistant.

    Paramètres
    ----------
    Aucun paramètre externe. Un id arbitraire (123456789) est utilisé.

    Retour
    ------
    None
        Le test confirme que :
        - modifier_qrc déclenche l’exception QRCodeNotFoundError.

    Notes
    -----
    Ce test valide la gestion d’erreur liée à l’absence du QR code ciblé.
    """
    dao = QRCodeDao()
    with pytest.raises(QRCodeNotFoundError):
        dao.modifier_qrc(123456789, "u1", url="x")


def test_modifier_qrc_raises_unauthorized():
    """
    Teste la modification d’un QR code par un utilisateur non propriétaire.

    Paramètres
    ----------
    Aucun paramètre externe. Un QR code est créé, puis modifié avec un id_user
    différent de celui associé au QR code.

    Retour
    ------
    None
        Le test vérifie que :
        - l’appel à modifier_qrc déclenche UnauthorizedError.

    Notes
    -----
    Ce cas confirme la protection contre les modifications non autorisées.
    """
    dao = QRCodeDao()

    q = dao.creer_qrc(Qrcode(id_qrcode=None, url="https://secure", id_proprietaire=3))
    with pytest.raises(UnauthorizedError):
        dao.modifier_qrc(id_qrcode=q.id_qrcode, url="x", id_user=4)


def test_supprimer_returns_true_or_false():
    """
    Teste le comportement de la suppression d’un QR code.

    Paramètres
    ----------
    Aucun paramètre externe. Deux cas sont testés :
    - suppression réelle,
    - suppression sur id inexistant.

    Retour
    ------
    None
        Le test confirme que :
        - supprimer_qrc renvoie True lorsque la ligne est supprimée,
        - renvoie False lorsque l’id n’existe pas.

    Notes
    -----
    Le test sépare explicitement le cas succès et le cas échec.
    """
    dao = QRCodeDao()

    q1 = dao.creer_qrc(Qrcode(id_qrcode=None, url="https://todel", id_proprietaire=3))
    assert dao.supprimer_qrc(q1.id_qrcode)

    assert dao.supprimer_qrc(999999) is False


def test_lister_par_proprietaire_ok():
    """
    Teste la récupération des QR codes appartenant à un utilisateur existant.

    Paramètres
    ----------
    Aucun paramètre externe. Le test utilise l’utilisateur id=3
    défini dans pop_db_test.sql.

    Retour
    ------
    None
        Le test vérifie :
        - que la liste contient exactement 1 QR code,
        - que l’objet retourné est un Qrcode,
        - que l’URL correspond à la valeur attendue.

    Notes
    -----
    La base de tests contient un QR code pour l’utilisateur id=3.
    """
    dao = QRCodeDao()
    id_user_3 = 3
    
    resultats = dao.lister_par_proprietaire(id_user_3)
    
    assert isinstance(resultats, list)
    assert len(resultats) == 1
    assert isinstance(resultats[0], Qrcode)
    assert resultats[0].url == "https://t.local/u3/c"


def test_lister_par_proprietaire_aucun_resultat():
    """
    Teste la récupération des QR codes pour un utilisateur n’ayant aucun QR code.

    Paramètres
    ----------
    Aucun paramètre externe. Un id inexistant (99999) est utilisé.

    Retour
    ------
    None
        Le test valide que la fonction renvoie une liste vide.

    Notes
    -----
    Aucun QR code ne doit être retourné pour un id utilisateur inexistant.
    """
    dao = QRCodeDao()
    id_user_inexistant = 99999
    
    resultats = dao.lister_par_proprietaire(id_user_inexistant)
    
    assert isinstance(resultats, list)
    assert len(resultats) == 0



if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
