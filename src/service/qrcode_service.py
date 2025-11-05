from typing import List, Optional
from datetime import datetime
from business_object.qr_code import Qrcode  # ta classe métier
from dao.qrcode_dao import QRCodeDao
from utils.qrcode_generator import generate_and_save_qr_png, filepath_to_public_url
import os

# assume env/config
QR_OUTPUT_DIR = os.getenv("QRCODE_OUTPUT_DIR", "static/qrcodes")
# Lit l'URL de scan depuis l'env (utilisée si type_ is True)
SCAN_BASE = os.getenv("SCAN_BASE_URL")


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

    def creer_qrc(
        self,
        url: str,
        id_proprietaire: str,
        type_: bool = True,
        couleur: Optional[str] = None,
        logo: Optional[str] = None,
    ) -> Optional[Qrcode]:
        
        # 1) Créer l'objet métier et le sauvegarder en base
        qrcode = Qrcode(
            id_qrcode=None,
            url=url, # URL de destination finale
            id_proprietaire=id_proprietaire,
            date_creation=None,
            type=type_, # bool : True = suivi, False = classique
            couleur=couleur,
            logo=logo,
        )
        created_qr = self.dao.creer_qrc(qrcode)
        if not created_qr:
            raise RuntimeError("Échec de création du QR code en base")

        # --- MODIFIÉ : Logique conditionnelle pour l'URL à encoder ---
        
        scan_url = None # Sera défini uniquement si le suivi est actif
        
        if type_ is True:
            # --- CAS 1: QR Code avec Suivi (Dynamique) ---
            # L'URL à encoder dans l'image est notre URL de scan
            if not SCAN_BASE:
                 raise RuntimeError("SCAN_BASE_URL n'est pas configuré dans .env pour un QR code suivi.")
            
            scan_url = f"{SCAN_BASE.rstrip('/')}/{created_qr.id_qrcode}"
            payload_url = scan_url
        else:
            # --- CAS 2: QR Code Classique (Statique) ---
            # L'URL à encoder dans l'image est l'URL de destination finale
            payload_url = created_qr.url # ou juste `url`

        # --- Fin de la modification ---


        # 3) Générer et sauvegarder l'image en utilisant la 'payload_url'
        saved_path = generate_and_save_qr_png(
            payload_url, # Encode soit l'URL de scan, soit l'URL finale
            out_dir=QR_OUTPUT_DIR,
            filename=f"qrcode_{created_qr.id_qrcode}.png",
            fill_color=couleur or "black",
            logo_path=logo,
            logo_scale=0.18,
        )

        # 4) Attacher les métadonnées à l'objet retourné
        public_url = filepath_to_public_url(saved_path)
        created_qr._image_path = saved_path
        created_qr._image_url = public_url
        created_qr._scan_url = scan_url # Sera None si c'est un QR classique

        return created_qr

    def trouver_qrc_par_id_user(self, id_user: str) -> List[Qrcode]:
        """Retourne tous les QR codes appartenant à un utilisateur."""
        # Convertit l'id_user (qui vient de l'API en str) en int pour le DAO
        try:
            user_id_int = int(id_user)
        except ValueError:
            return [] # Ou lever une erreur si un id non-numérique est invalide
        return self.dao.lister_par_proprietaire(user_id_int)


    def supprimer_qrc(self, id_qrcode: int, id_user: str) -> bool:
        """
        Supprime un QR code après vérification du propriétaire.
        """
        qr = self.dao.trouver_par_id(id_qrcode) # 'trouver_par_id' semble plus correct ici
        if not qr:
            raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")
        
        # S'assurer que les ID sont comparés au même type (ex: str vs str ou int vs int)
        if str(qr.id_proprietaire) != str(id_user):
            raise UnauthorizedError("Suppression non autorisée.")
        
        # Logique de suppression de fichier (optionnel mais propre)
        try:
            file_name = f"qrcode_{id_qrcode}.png"
            file_path = os.path.join(QR_OUTPUT_DIR, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            # Ne pas bloquer la suppression en BDD si la suppression de fichier échoue
            print(f"Avertissement: n'a pas pu supprimer le fichier image {file_path}: {e}")

        return self.dao.supprimer(id_qrcode) # Assumer que le DAO a une méthode 'supprimer(id)'

    def modifier_qrc(self, id_qrcode: int, id_user: str,
                     url: Optional[str] = None, type_qrcode: Optional[bool] = None,
                     couleur: Optional[str] = None, logo: Optional[str] = None) -> Qrcode:
        """
        Modifie un QR code existant après vérification du propriétaire.
        NOTE: La modification du 'type' ou de 'l'url' devrait déclencher 
        une re-génération de l'image, ce qui n'est pas fait ici.
        """
        qr = self.dao.trouver_par_id(id_qrcode)
        if not qr:
            raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")
        
        if str(qr.id_proprietaire) != str(id_user):
            raise UnauthorizedError("Modification non autorisée.")

        return self.dao.modifier_qrc(
            id_qrcode=id_qrcode,
            url=url,
            type_=type_qrcode,
            couleur=couleur,
            logo=logo
        )
