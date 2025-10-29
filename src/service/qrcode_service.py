from typing import List, Optional

# Exceptions métier
class QRCodeNotFoundError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

class QRCodeService:
    """
    Service métier pour gérer les QR codes.
    Utilise un DAO pour la persistance (PostgreSQL ici).
    """

    def __init__(self, dao: 'QRCodeDao'):
        self.dao = dao

    def creer_qrc(self, url: str, type_qrcode: bool, couleur: str, logo: str, id_proprietaire: str, id_qrcode: int) -> 'Qrcode':
        """
        Crée un QRCode, le sauvegarde via le DAO et renvoie l'objet.
        id_qrcode doit être généré côté service ou client.
        """
        from datetime import datetime
        q = Qrcode(
            id_qrcode=id_qrcode,
            url=url,
            id_proprietaire=id_proprietaire,
            date_creation=datetime.utcnow(),
            type_qrcode=type_qrcode,
            couleur=couleur,
            logo=logo
        )
        self.dao.créer_qrc(q)
        return q

    def trouver_qrc_par_id_user(self, id_user: str) -> List['Qrcode']:
        """Retourne la liste des QRCodes appartenant à l’utilisateur."""
        return self.dao.trouver_par_id(id_user)

    def supprimer_qrc(self, qrcode: 'Qrcode') -> bool:
        """Supprime un QRCode via le DAO."""
        return self.dao.supprimer(qrcode)

    def verifier_proprietaire(self, qrcode: 'Qrcode', id_user: str) -> bool:
        """Vérifie que l'utilisateur est bien le propriétaire du QRCode."""
        return qrcode._Qrcode__id_proprietaire == id_user

    def modifier_qrc(self, id_qrcode: int, id_user: str,
                     url: Optional[str] = None, type_qrcode: Optional[bool] = None,
                     couleur: Optional[str] = None, logo: Optional[str] = None) -> 'Qrcode':
        """
        Modifie un QRCode existant après vérification du propriétaire.
        Lève QRCodeNotFoundError ou UnauthorizedError si problème.
        """
        return self.dao.modifier_qrc(
            id_qrcode=id_qrcode,
            id_user=id_user,
            url=url,
            type_=type_,
            couleur=couleur,
            logo=logo
        )
