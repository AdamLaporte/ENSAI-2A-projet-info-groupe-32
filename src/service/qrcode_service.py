from typing import List, Optional
from datetime import datetime
from business_object.qr_code import Qrcode  # ta classe métier
from dao.qrcode_dao import QRCodeDao
from utils.qrcode_generator import generate_and_save_qr_png, filepath_to_public_url
import os

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

    def creer_qrc(
        self,
        url: str,
        id_proprietaire: str,
       type_qrcode: bool = True,
        couleur: Optional[str] = None,
        logo: Optional[str] = None,
    ) -> Optional[Qrcode]:
        
        # 1) Créer l'objet métier et le sauvegarder en base
        qrcode = Qrcode(
            id_qrcode=None,
            url=url, # URL de destination finale
            id_proprietaire=id_proprietaire,
            date_creation=None,
            type_qrcode=type_, # bool : True = suivi, False = classique
            couleur=couleur,
            logo=logo,
        )
        created_qr = self.dao.creer_qrc(qrcode)
        if not created_qr:
            raise RuntimeError("Échec de création du QR code en base")

        # --- MODIFIÉ : Logique conditionnelle pour l'URL à encoder ---
        
        scan_url = None # Sera défini uniquement si le suivi est actif
        
        if type_qrcode is True:
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

        return self.dao.supprimer_qrc(id_qrcode) # Le DAO a une méthode 'supprimer_qrc(id)'

    def modifier_qrc(self, id_qrcode: int, id_user: str,
                     url: Optional[str] = None, type_qrcode: Optional[bool] = None,
                     couleur: Optional[str] = None, logo: Optional[str] = None) -> Qrcode:
        """
        Modifie un QR code existant après vérification du propriétaire.
        Si l'URL ou le type d'un QR 'non-suivi' est modifié,
        l'image PNG est re-générée.
        """
        
        # 1. Vérifier les droits
        qr = self.dao.trouver_par_id(id_qrcode)
        if not qr:
            raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")
        
        if str(qr.id_proprietaire) != str(id_user):
            raise UnauthorizedError("Modification non autorisée.")

        # 2. Déterminer si une re-génération est nécessaire
        # (on ne re-génère que si c'est un QR statique (type_qrcode==False)
        # OU si on le transforme en QR statique)
        
        payload_url_a_encoder = None
        regenerate_image = False

        nouvelle_url = url if url is not None else qr.url
        nouveau_type = type_qrcode if type_qrcode is not None else qr.type_qrcode

        if nouveau_type_qrcode is False:
            # Cas 1: C'est (ou ça devient) un QR Statique.
            # L'image DOIT contenir l'URL de destination.
            
            if (qr.type_qrcode is True): # Il passe de Dynamique -> Statique
                regenerate_image = True
                payload_url_a_encoder = nouvelle_url
            
            elif (url is not None and url != qr.url): # Il était Statique et son URL change
                regenerate_image = True
                payload_url_a_encoder = nouvelle_url
            
            elif (couleur is not None and couleur != qr.couleur): # Statique et couleur change
                 regenerate_image = True
                 payload_url_a_encoder = nouvelle_url

            elif (logo is not None and logo != qr.logo): # Statique et logo change
                 regenerate_image = True
                 payload_url_a_encoder = nouvelle_url

        else:
             # Cas 2: C'est (ou ça devient) un QR Dynamique.
             # L'image DOIT contenir l'URL de scan.
             scan_url = f"{SCAN_BASE.rstrip('/')}/{qr.id_qrcode}"

             if (qr.type_qrcode is False): # Il passe de Statique -> Dynamique
                regenerate_image = True
                payload_url_a_encoder = scan_url
             
             elif (couleur is not None and couleur != qr.couleur): # Dynamique et couleur change
                regenerate_image = True
                payload_url_a_encoder = scan_url

             elif (logo is not None and logo != qr.logo): # Dynamique et logo change
                regenerate_image = True
                payload_url_a_encoder = scan_url


        # 3. Re-générer l'image si nécessaire
        if regenerate_image:
            print(f"Re-génération de l'image pour QR {id_qrcode}...")
            
            # Utilise les nouvelles valeurs (si fournies) ou les anciennes
            nouveau_couleur = couleur if couleur is not None else qr.couleur
            nouveau_logo = logo if logo is not None else qr.logo

            generate_and_save_qr_png(
                payload_url_a_encoder,
                out_dir=QR_OUTPUT_DIR,
                filename=f"qrcode_{qr.id_qrcode}.png", # Ecrase l'ancien
                fill_color=nouveau_couleur or "black",
                logo_path=nouveau_logo,
            )

        
        return self.dao.modifier_qrc(
            id_qrcode=id_qrcode,
            id_user=id_user, # Le DAO attend un int
            url=url,
            type_qrcode=type_qrcode,
            couleur=couleur,
            logo=logo
        )