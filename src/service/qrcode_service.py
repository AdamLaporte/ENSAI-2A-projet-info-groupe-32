from typing import List, Optional
from datetime import datetime
from business_object.qr_code import Qrcode  # ta classe métier
from dao.qrcode_dao import QRCodeDao


class QRCodeNotFoundError(Exception):
    """Erreur levée si le QR code n'existe pas."""
    pass


class UnauthorizedError(Exception):
    """Erreur levée si l'utilisateur n'est pas le propriétaire du QR code."""
    pass


class QRCodeService:
    """Service métier pour la gestion des QR codes."""

    def __init__(self, dao: QRCodeDao):
        self.dao = dao

    def creer_qrc(self, url: str, id_proprietaire: str,
                  type_: bool = False, couleur: Optional[str] = None,
                  logo: Optional[str] = None) -> Qrcode:
        """
        Crée un QR code et le sauvegarde via le DAO.
        L'identifiant est généré automatiquement par la base.
        """
        qrcode = Qrcode(
            id_qrcode=None,
            url=url,
            id_proprietaire=id_proprietaire,
            date_creation=datetime.utcnow(),
            type=type_,
            couleur=couleur or "noir",
            logo=logo
        )
        created_qr = self.dao.creer_qrc(qrcode)
        return created_qr

    def trouver_qrc_par_id_user(self, id_user: str) -> List[Qrcode]:
        """Retourne tous les QR codes appartenant à un utilisateur."""
        return self.dao.trouver_qrc_par_id_user(id_user)

    def supprimer_qrc(self, id_qrcode: int, id_user: str) -> bool:
        """
        Supprime un QR code après vérification du propriétaire.
        """
        qr = self.dao.trouver_qrc_par_id_qrc(id_qrcode)
        if not qr:
            raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")
        if qr.id_proprietaire != id_user:
            raise UnauthorizedError("Suppression non autorisée.")
        return self.dao.supprimer_qrc(qr)

    def modifier_qrc(self, id_qrcode: int, id_user: str,
                     url: Optional[str] = None, type_: Optional[bool] = None,
                     couleur: Optional[str] = None, logo: Optional[str] = None) -> Qrcode:
        """
        Modifie un QR code existant après vérification du propriétaire.
        """
        qr = self.dao.trouver_qrc_par_id(id_qrcode)
        if not qr:
            raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")
        if qr.id_proprietaire != id_user:
            raise UnauthorizedError("Modification non autorisée.")

        return self.dao.modifier_qrc(
            id_qrcode=id_qrcode,
            url=url,
            type_=type_,
            couleur=couleur,
            logo=logo
        )
