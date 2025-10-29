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

    @log
    def creer_qrc(self, qrcode: Qrcode) -> Optional[Qrcode]:
        """
        Insère un QRCode en base et renvoie l'objet Qrcode créé avec id.
        """
        try:
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO qrcodes (url, id_proprietaire, type, couleur, logo)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id_qrcode, date_creation;
                        """,
                        (
                            qrcode.url,
                            qrcode.id_proprietaire,
                            qrcode.type,
                            qrcode.couleur,
                            qrcode.logo,
                        ),
                    )
                    res = cur.fetchone()
                    if not res:
                        return None

                    # Supporte tuple OU dict selon le type de curseur
                    if isinstance(res, dict):
                        new_id = res["id_qrcode"]
                        date_creation = res["date_creation"]
                    else:
                        new_id, date_creation = res

                    #  Propriétés read-only : on met à jour les attributs privés
                    qrcode._id_qrcode = new_id
                    qrcode._date_creation = date_creation

                # commit explicite (plus sûr selon ta config)
                conn.commit()

            return qrcode

        except Exception as e:
            logger.exception("Erreur lors de creer_qrc : %s", e)
            return None

    @log
    def trouver_qrc_par_id_user(self, id_user: str) -> List[Qrcode]:
        """
        Renvoie la liste des Qrcode pour un propriétaire donné.
        """
        try:
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo
                        FROM qrcodes
                        WHERE id_proprietaire = %s
                        ORDER BY date_creation DESC;
                        """,
                        (id_user,),
                    )
                    rows = cur.fetchall()
            qrcodes: List[Qrcode] = []
            for row in rows:
                q = Qrcode(
                    id_qrcode=row["id_qrcode"],
                    url=row["url"],
                    id_proprietaire=row["id_proprietaire"],
                    date_creation=row["date_creation"],
                    type=row.get("type"),
                    couleur=row.get("couleur"),
                    logo=row.get("logo"),
                )
                qrcodes.append(q)
            return qrcodes
        except Exception as e:
            logger.exception("Erreur lors de trouver_par_id : %s", e)
            raise

    def supprimer_qrc(self, id_qrcode: int) -> bool:
        """
        Supprime un QRCode par id. Retourne True si une ligne supprimée.
        """
        with self._db.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM qrcode WHERE id_qrcode = %s", (id_qrcode,))
                return cur.rowcount > 0

    def trouver_qrc_par_id_qrc(self, id_qrcode: int) -> Optional[Qrcode]:
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
                qrcodes.append(q)
            return qrcodes
        except Exception as e:
            logger.exception("Erreur lors de trouver_par_id : %s", e)
            raise

    @log
    def modifier_qrc(self,
                     id_qrcode: int,
                     url: Optional[str] = None,
                     type_qrcode: Optional[bool] = None,
                     couleur: Optional[str] = None,
                     logo: Optional[str] = None,
                     ) -> Optional[Qrcode]:
        """
        Met à jour les champs fournis et retourne l’objet mis à jour, ou None si id introuvable.
        """

        try:
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    # Vérifier existence et propriétaire
                    cur.execute(
                        "SELECT id_proprietaire FROM qrcodes WHERE id_qrcode = %s;",
                        (id_qrcode,),
                    )
                    row = cur.fetchone()
                    if not row:
                        raise QRCodeNotFoundError(
                            f"QR code {id_qrcode} introuvable.")
                    if row["id_proprietaire"] != id_user:
                        raise UnauthorizedError(
                            "Seul le propriétaire peut modifier ce QR code.")

                    # Mise à jour (on utilise COALESCE pour garder les valeurs non fournies)
                    cur.execute(
                        """
                        UPDATE qrcodes
                        SET url = COALESCE(%s, url),
                            type = COALESCE(%s, type),
                            couleur = COALESCE(%s, couleur),
                            logo = COALESCE(%s, logo)
                        WHERE id_qrcode = %s
                        RETURNING id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo;
                        """,
                        (url, type_, couleur, logo, id_qrcode),
                    )
                    updated = cur.fetchone()
            if not updated:
                raise QRCodeNotFoundError(
                    f"QR code {id_qrcode} introuvable après tentative de mise à jour.")
            # reconstruire l'objet métier et le renvoyer
            return Qrcode(
                id_qrcode=updated["id_qrcode"],
                url=updated["url"],
                id_proprietaire=updated["id_proprietaire"],
                date_creation=updated["date_creation"],
                type=updated.get("type"),
                couleur=updated.get("couleur"),
                logo=updated.get("logo"),
            )
        except (QRCodeNotFoundError, UnauthorizedError):
            # propager ces erreurs pour que le service puisse les traduire en 404/403
            raise
        except Exception as e:
            logger.exception("Erreur lors de modifier_qrc : %s", e)
            raise

    @log
    def supprimer(self, qrcode: Qrcode) -> bool:
        """
        Supprime un QRCode par son identifiant. Retourne True si ligne supprimée.
        """
        try:
            qid = qrcode.id_qrcode
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM qrcodes WHERE id_qrcode = %s;", (qid,))
                    deleted = cur.rowcount > 0
            return bool(deleted)
        except Exception as e:
            logger.exception("Erreur lors de supprimer : %s", e)
            return False
