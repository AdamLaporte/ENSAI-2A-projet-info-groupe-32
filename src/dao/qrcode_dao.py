from typing import List, Optional

from dao.db_connexion import DBConnection

from business_object.qr_code import Qrcode

class QRCodeNotFoundError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class QRCodeDao:
    """DAO pour la gestion des QR codes, utilisant la connexion partagée à PostgreSQL."""

    def __init__(self):
        # On récupère la connexion déjà ouverte par DBConnection 
        self.conn = DBConnection().connection

    def créer_qrc(self, qrcode: Qrcode) -> bool:
        """Insère ou met à jour un QRCode."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO qrcodes (id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_qrcode) DO UPDATE
                SET url = EXCLUDED.url,
                    type = EXCLUDED.type,
                    couleur = EXCLUDED.couleur,
                    logo = EXCLUDED.logo
            """,
                (
                    qrcode.get_id(),
                    qrcode.get_url(),
                    qrcode._Qrcode__id_proprietaire,
                    qrcode._Qrcode__date_creation,
                    qrcode._Qrcode__type,
                    qrcode._Qrcode__couleur,
                    qrcode._Qrcode__logo,
                ),
            )
        self.conn.commit()
        return True

    def trouver_par_id(self, id_user: str) -> List[Qrcode]:
        """Retourne tous les QR codes d’un utilisateur donné."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo
                FROM qrcodes
                WHERE id_proprietaire = %s
            """,
                (id_user,),
            )
            rows = cur.fetchall()

        qrcodes = [
            Qrcode(
                id_qrcode=row["id_qrcode"],
                url=row["url"],
                id_proprietaire=row["id_proprietaire"],
                date_creation=row["date_creation"],
                type=row["type"],
                couleur=row["couleur"],
                logo=row["logo"],
            )
            for row in rows
        ]
        return qrcodes

    def modifier_qrc(
        self,
        id_qrcode: int,
        id_user: str,
        url: Optional[str] = None,
        type_: Optional[bool] = None,
        couleur: Optional[str] = None,
        logo: Optional[str] = None,
    ) -> Qrcode:
        """Modifie un QR code existant après vérification du propriétaire."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id_proprietaire, url, date_creation, type, couleur, logo
                FROM qrcodes
                WHERE id_qrcode = %s
            """,
                (id_qrcode,),
            )
            row = cur.fetchone()
            if not row:
                raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")
            if row["id_proprietaire"] != id_user:
                raise UnauthorizedError("Seul le propriétaire peut modifier ce QR code.")

            cur.execute(
                """
                UPDATE qrcodes
                SET url = COALESCE(%s, url),
                    type = COALESCE(%s, type),
                    couleur = COALESCE(%s, couleur),
                    logo = COALESCE(%s, logo)
                WHERE id_qrcode = %s
            """,
                (url, type_, couleur, logo, id_qrcode),
            )
            self.conn.commit()

        # reconstruit le Qrcode mis à jour
        return Qrcode(
            id_qrcode=id_qrcode,
            url=url if url is not None else row["url"],
            id_proprietaire=row["id_proprietaire"],
            date_creation=row["date_creation"],
            type=type_ if type_ is not None else row["type"],
            couleur=couleur if couleur is not None else row["couleur"],
            logo=logo if logo is not None else row["logo"],
        )

    def supprimer(self, qrcode: Qrcode) -> bool:
        """Supprime un QRCode par son identifiant."""
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM qrcodes WHERE id_qrcode = %s", (qrcode.get_id(),))
            deleted = cur.rowcount > 0
        self.conn.commit()
        return deleted
