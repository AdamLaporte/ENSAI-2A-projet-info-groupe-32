import logging
from typing import List, Optional

from dao.db_connection import DBConnection
from business_object.qr_code import Qrcode

logger = logging.getLogger(__name__)


class QRCodeNotFoundError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class QRCodeDao:
    """
    DAO pour la table `qrcode` (alignée sur init_db.sql).
    - Lecture via propriétés de Qrcode
    - Les méthodes de création et modification retournent l’objet (avec id)
    - Les méthodes de suppression retournent un bool
    """

    def __init__(self):
        self._db = DBConnection()

    def creer_qrc(self, qrcode: Qrcode) -> Qrcode:
        """
        Insère un QRCode en base et retourne l'objet avec id renseigné.
        Colonne booléenne: type_qrcode (schéma).
        """
        with self._db.connection as conn:
            with conn.cursor() as cur:
                if qrcode.id_qrcode is not None:
                    cur.execute(
                        """
                        INSERT INTO qrcode (id_qrcode, url, id_proprietaire, type_qrcode, couleur, logo)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id_qrcode
                        """,
                        (
                            qrcode.id_qrcode,
                            qrcode.url,
                            int(qrcode.id_proprietaire),
                            qrcode.type,
                            qrcode.couleur,
                            qrcode.logo,
                        ),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO qrcode (url, id_proprietaire, type_qrcode, couleur, logo)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id_qrcode
                        """,
                        (
                            qrcode.url,
                            int(qrcode.id_proprietaire),
                            qrcode.type,
                            qrcode.couleur,
                            qrcode.logo,
                        ),
                    )
                new_id = cur.fetchone()["id_qrcode"]
                # Hydrate l’objet (accès interne assumé par ton modèle)
                qrcode._id_qrcode = new_id  # type: ignore[attr-defined]
                return qrcode

    def supprimer_qrc(self, id_qrcode: int) -> bool:
        """
        Supprime un QRCode par id. Retourne True si une ligne supprimée.
        """
        with self._db.connection as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM qrcode WHERE id_qrcode = %s", (id_qrcode,))
                return cur.rowcount > 0

    def trouver_par_id(self, id_qrcode: int) -> Optional[Qrcode]:
        """
        Retourne un Qrcode par id, ou None si introuvable.
        """
        with self._db.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_qrcode, url, id_proprietaire, date_creation, type_qrcode, couleur, logo
                    FROM qrcode
                    WHERE id_qrcode = %s
                    """,
                    (id_qrcode,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return Qrcode(
                    id_qrcode=row["id_qrcode"],
                    url=row["url"],
                    id_proprietaire=str(row["id_proprietaire"]),
                    date_creation=row["date_creation"],
                    type=row["type_qrcode"],
                    couleur=row["couleur"],
                    logo=row["logo"],
                )

    def lister_par_proprietaire(self, id_user: int) -> List[Qrcode]:
        """
        Liste les QR codes d’un propriétaire, triés par date_creation DESC.
        """
        with self._db.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_qrcode, url, id_proprietaire, date_creation, type_qrcode, couleur, logo
                    FROM qrcode
                    WHERE id_proprietaire = %s
                    ORDER BY date_creation DESC
                    """,
                    (id_user,),
                )
                rows = cur.fetchall()
                return [
                    Qrcode(
                        id_qrcode=r["id_qrcode"],
                        url=r["url"],
                        id_proprietaire=str(r["id_proprietaire"]),
                        date_creation=r["date_creation"],
                        type=r["type_qrcode"],
                        couleur=r["couleur"],
                        logo=r["logo"],
                    )
                    for r in rows
                ]

    def mettre_a_jour(
        self,
        id_qrcode: int,
        url: Optional[str] = None,
        type_qrcode: Optional[bool] = None,
        couleur: Optional[str] = None,
        logo: Optional[str] = None,
    ) -> Optional[Qrcode]:
        """
        Met à jour les champs fournis et retourne l’objet mis à jour, ou None si id introuvable.
        """
        sets = []
        params = []
        if url is not None:
            sets.append("url = %s")
            params.append(url)
        if type_qrcode is not None:
            sets.append("type_qrcode = %s")
            params.append(type_qrcode)
        if couleur is not None:
            sets.append("couleur = %s")
            params.append(couleur)
        if logo is not None:
            sets.append("logo = %s")
            params.append(logo)

        if not sets:
            # Rien à mettre à jour → renvoyer l’état actuel
            return self.trouver_par_id(id_qrcode)

        params.append(id_qrcode)
        with self._db.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE qrcode
                    SET {", ".join(sets)}
                    WHERE id_qrcode = %s
                    RETURNING id_qrcode, url, id_proprietaire, date_creation, type_qrcode, couleur, logo
                    """,
                    params,
                )
                row = cur.fetchone()
                if not row:
                    return None
                return Qrcode(
                    id_qrcode=row["id_qrcode"],
                    url=row["url"],
                    id_proprietaire=str(row["id_proprietaire"]),
                    date_creation=row["date_creation"],
                    type=row["type_qrcode"],
                    couleur=row["couleur"],
                    logo=row["logo"],
                )
