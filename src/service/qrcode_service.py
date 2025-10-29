from typing import List, Optional
from datetime import datetime
from business_object.qr_code import Qrcode  # ta classe métier
from dao.qrcode_dao import QRCodeDao
from utils.qrcode_generator import generate_and_save_qr_png, filepath_to_public_url
import os

# assume env/config
QR_OUTPUT_DIR = os.getenv("QRCODE_OUTPUT_DIR", "static/qrcodes")
TRACKING_BASE = os.getenv("TRACKING_BASE_URL", "https://monapi.example.com/r")


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
                  type_: bool = True, couleur: Optional[str] = None,
                  logo: Optional[str] = None) -> Optional[Qrcode]:

        qrcode = Qrcode(
            id_qrcode=None,
            url=url,
            id_proprietaire=id_proprietaire,
            date_creation=None,
            type=type_,
            couleur=couleur,
            logo=logo,
        )

        created_qr = self.dao.creer_qrc(qrcode)
        if not created_qr:
            raise RuntimeError("Échec de création du QR code en base")

        tracking_url = f"{TRACKING_BASE}/{created_qr.id_qrcode}"

        saved_path = generate_and_save_qr_png(
            tracking_url,
            out_dir=QR_OUTPUT_DIR,
            filename=f"qrcode_{created_qr.id_qrcode}.png",
            fill_color=couleur or "black",
            logo_path=logo,
            logo_scale=0.18,
        )

        public_url = filepath_to_public_url(saved_path)
        created_qr._image_path = saved_path
        created_qr._image_url = public_url

    # (optionnel) persister le chemin image dans la base
    # self.dao.update_image_path(created_qr.id_qrcode, public_url)

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
