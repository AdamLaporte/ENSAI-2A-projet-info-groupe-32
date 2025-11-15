from typing import List, Optional
from datetime import datetime
from business_object.qr_code import Qrcode  # ta classe métier
from dao.qrcode_dao import QRCodeDao
from utils.qrcode_generator import generate_and_save_qr_png, filepath_to_public_url
import os
from utils.log_decorator import log

# assume env/config
QR_OUTPUT_DIR = os.getenv("QRCODE_OUTPUT_DIR", "static/qrcodes")
# Lit l'URL de scan depuis l'env (utilisée si type_qrcode is True)
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

    @log
    def creer_qrc(
        self,
        url: str,
        id_proprietaire: str,
        type_qrcode: bool = True,
        couleur: Optional[str] = None,
        logo: Optional[str] = None,
    ) -> Optional[Qrcode]:
        """
        Crée un QR code et génère son image PNG.

        Paramètres
        ----------
        url : str
            URL de destination finale associée au QR code.
        id_proprietaire : str
            Identifiant du propriétaire du QR code (format chaîne, converti en int par le DAO).
        type_qrcode : bool, par défaut True
            - True : QR code dynamique avec suivi (utilise une URL de scan).
            - False : QR code statique (encode directement l’URL finale).
        couleur : str, optionnel
            Couleur du QR code lors de la génération de l’image.
        logo : str, optionnel
            Chemin vers un fichier image à incruster au centre du QR code.

        Retour
        ------
        Optional[Qrcode]
            - Renvoie l'objet Qrcode complet après insertion et génération de l’image.
            - Lève une RuntimeError si la création échoue en base.

        Notes
        -----
        - Le QR code dynamique encode une URL de scan basée sur SCAN_BASE.
        - Le QR code statique encode directement `url`.
        - L’image PNG est générée dans `QR_OUTPUT_DIR`, puis rendue accessible
        via son URL publique.
        - Les attributs internes `_image_path`, `_image_url`, `_scan_url`
        sont attachés à l'objet retourné.
        """
        qrcode = Qrcode(
            id_qrcode=None,
            url=url,
            id_proprietaire=id_proprietaire,
            date_creation=None,
            type_qrcode=type_qrcode,
            couleur=couleur,
            logo=logo,
        )
        created_qr = self.dao.creer_qrc(qrcode)
        if not created_qr:
            raise RuntimeError("Échec de création du QR code en base")

        scan_url = None

        if type_qrcode is True:
            if not SCAN_BASE:
                raise RuntimeError("SCAN_BASE_URL n'est pas configuré dans .env pour un QR code suivi.")
            scan_url = f"{SCAN_BASE.rstrip('/')}/{created_qr.id_qrcode}"
            payload_url = scan_url
        else:
            payload_url = created_qr.url

        saved_path = generate_and_save_qr_png(
            payload_url,
            out_dir=QR_OUTPUT_DIR,
            filename=f"qrcode_{created_qr.id_qrcode}.png",
            fill_color=couleur or "black",
            logo_path=logo,
            logo_scale=0.18,
        )

        public_url = filepath_to_public_url(saved_path)
        created_qr._image_path = saved_path
        created_qr._image_url = public_url
        created_qr._scan_url = scan_url

        return created_qr


    def trouver_qrc_par_id_user(self, id_user: str) -> List[Qrcode]:
        """
        Récupère tous les QR codes appartenant à un utilisateur.

        Paramètres
        ----------
        id_user : str
            Identifiant de l'utilisateur fourni par l’API (chaîne de caractères).

        Retour
        ------
        List[Qrcode]
            - Liste des QR codes appartenant à l’utilisateur.
            - Liste vide si id_user n’est pas numérique ou ne correspond à aucun utilisateur.

        Notes
        -----
        L'id_user est converti en entier avant interrogation du DAO.
        """
        try:
            user_id_int = int(id_user)
        except ValueError:
            return []
        return self.dao.lister_par_proprietaire(user_id_int)


    def supprimer_qrc(self, id_qrcode: int, id_user: int) -> bool:
        """
        Supprime un QR code après vérification de son propriétaire.

        Paramètres
        ----------
        id_qrcode : int
            Identifiant du QR code à supprimer.
        id_user : int
            Identifiant de l'utilisateur tentant la suppression.

        Retour
        ------
        bool
            - True si la suppression en base est réalisée.
            - False sinon.

        Notes
        -----
        - Vérifie que le QR code existe, sinon lève QRCodeNotFoundError.
        - Vérifie que l’utilisateur est bien propriétaire, sinon lève UnauthorizedError.
        - Tente de supprimer le fichier PNG associé (sans bloquer la suppression BDD).
        """
        qr = self.dao.trouver_qrc_par_id_qrc(id_qrcode)
        if not qr:
            raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")

        if str(qr.id_proprietaire) != str(id_user):
            raise UnauthorizedError("Suppression non autorisée.")

        try:
            file_name = f"qrcode_{id_qrcode}.png"
            file_path = os.path.join(QR_OUTPUT_DIR, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Avertissement: n'a pas pu supprimer le fichier image {file_path}: {e}")

        return self.dao.supprimer_qrc(id_qrcode)


    def trouver_qrc_par_id(self, id_qrcode: int) -> Optional[Qrcode]:
        """
        Trouve un QR code à partir de son identifiant.

        Paramètres
        ----------
        id_qrcode : int
            Identifiant du QR code recherché.

        Retour
        ------
        Optional[Qrcode]
            L'objet Qrcode correspondant ou None si non trouvé.

        Notes
        -----
        Le service délègue directement au DAO.
        """
        return self.dao.trouver_qrc_par_id_qrc(id_qrcode)


    def modifier_qrc(
        self,
        id_qrcode: int,
        id_user: int,
        url: Optional[str] = None,
        type_qrcode: Optional[bool] = None,
        couleur: Optional[str] = None,
        logo: Optional[str] = None
    ) -> Qrcode:
        """
        Modifie un QR code existant après vérification du propriétaire.

        Paramètres
        ----------
        id_qrcode : int
            Identifiant du QR code à modifier.
        id_user : int
            Identifiant de l’utilisateur tentant la modification.
        url : str, optionnel
            Nouvelle URL finale associée au QR code.
        type_qrcode : bool, optionnel
            Type du QR code :
            - True : dynamique (suivi)
            - False : statique
        couleur : str, optionnel
            Nouvelle couleur du QR code.
        logo : str, optionnel
            Nouveau logo à intégrer dans l’image.

        Retour
        ------
        Qrcode
            L’objet mis à jour après passage en base.

        Notes
        -----
        - Lève QRCodeNotFoundError si id_qrcode est absent.
        - Lève UnauthorizedError si l’utilisateur n’est pas propriétaire.
        - Détermine si l’image doit être régénérée selon :
            * le changement d’URL (pour un QR statique),
            * le changement de type,
            * le changement de couleur,
            * le changement de logo.
        - Si nécessaire, la nouvelle image PNG écrase l’ancienne.
        """
        qr = self.dao.trouver_qrc_par_id_qrc(id_qrcode)
        if not qr:
            raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")

        if str(qr.id_proprietaire) != str(id_user):
            raise UnauthorizedError("Modification non autorisée.")

        payload_url_a_encoder = None
        regenerate_image = False

        nouvelle_url = url if url is not None else qr.url
        nouveau_type_qrcode = type_qrcode if type_qrcode is not None else qr.type_qrcode

        if nouveau_type_qrcode is False:
            if qr.type_qrcode is True:
                regenerate_image = True
                payload_url_a_encoder = nouvelle_url
            elif (url is not None and url != qr.url):
                regenerate_image = True
                payload_url_a_encoder = nouvelle_url
            elif (couleur is not None and couleur != qr.couleur):
                regenerate_image = True
                payload_url_a_encoder = nouvelle_url
            elif (logo is not None and logo != qr.logo):
                regenerate_image = True
                payload_url_a_encoder = nouvelle_url

        else:
            scan_url = f"{SCAN_BASE.rstrip('/')}/{qr.id_qrcode}"

            if qr.type_qrcode is False:
                regenerate_image = True
                payload_url_a_encoder = scan_url
            elif (couleur is not None and couleur != qr.couleur):
                regenerate_image = True
                payload_url_a_encoder = scan_url
            elif (logo is not None and logo != qr.logo):
                regenerate_image = True
                payload_url_a_encoder = scan_url

        if regenerate_image:
            print(f"Re-génération de l'image pour QR {id_qrcode}...")

            nouveau_couleur = couleur if couleur is not None else qr.couleur
            nouveau_logo = logo if logo is not None else qr.logo

            generate_and_save_qr_png(
                payload_url_a_encoder,
                out_dir=QR_OUTPUT_DIR,
                filename=f"qrcode_{qr.id_qrcode}.png",
                fill_color=nouveau_couleur or "black",
                logo_path=nouveau_logo,
            )

        return self.dao.modifier_qrc(
            id_qrcode=id_qrcode,
            id_user=id_user,
            url=url,
            type_qrcode=type_qrcode,
            couleur=couleur,
            logo=logo
        )
