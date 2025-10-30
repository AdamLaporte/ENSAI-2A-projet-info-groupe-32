import logging
from typing import List, Optional

from dao.db_connection import DBConnection
from business_object.qr_code import Qrcode

logger = logging.getLogger(__name__)


class QRCodeNotFoundError(Exception):
    """Erreur levée lorsqu’un QR code est introuvable."""
    pass


class UnauthorizedError(Exception):
    """Erreur levée lorsqu’un utilisateur tente de modifier un QR code qui ne lui appartient pas."""
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

    def creer_qrc(self, qrcode: Qrcode) -> Optional[Qrcode]:
        """
        Insère un QRCode en base et retourne l'objet avec id renseigné.
        Colonne booléenne : type_qrcode (schéma).
        """
        try:
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    if qrcode.id_qrcode is not None:
                        cur.execute(
                            """
                            INSERT INTO qrcode (id_qrcode, url, id_proprietaire, type_qrcode, couleur, logo)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id_qrcode, date_creation;
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
                            RETURNING id_qrcode, date_creation;
                            """,
                            (
                                qrcode.url,
                                int(qrcode.id_proprietaire),
                                qrcode.type,
                                qrcode.couleur,
                                qrcode.logo,
                            ),
                        )

                    res = cur.fetchone()
                    if not res:
                        raise Exception("Aucun ID retourné après insertion du QR code.")

                    # Supporte RealDictCursor ou tuple
                    if isinstance(res, dict):
                        new_id = res["id_qrcode"]
                        date_creation = res["date_creation"]
                    else:
                        new_id, date_creation = res

                    # Hydrate l’objet
                    qrcode._id_qrcode = new_id
                    qrcode._date_creation = date_creation

                conn.commit()

            logger.info(f"QR code créé avec succès : id={new_id}")
            return qrcode

        except Exception as e:
            logger.exception(f"Erreur lors de la création du QR code : {e}")
            return None

    def supprimer_qrc(self, id_qrcode: int) -> bool:
        """
        Supprime un QRCode par id. Retourne True si une ligne supprimée.
        """
        try:
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM qrcode WHERE id_qrcode = %s;", (id_qrcode,))
                    deleted = cur.rowcount > 0
                conn.commit()

            if deleted:
                logger.info(f"QR code {id_qrcode} supprimé avec succès.")
            else:
                logger.warning(f"Tentative de suppression d’un QR code inexistant : {id_qrcode}.")
            return deleted

        except Exception as e:
            logger.exception(f"Erreur lors de la suppression du QR code {id_qrcode} : {e}")
            return False

    def trouver_par_id(self, id_qrcode: int) -> Optional[Qrcode]:
        """
        Retourne un Qrcode par id, ou None si introuvable.
        """
        try:
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id_qrcode, url, id_proprietaire, date_creation, type_qrcode, couleur, logo
                        FROM qrcode
                        WHERE id_qrcode = %s;
                        """,
                        (id_qrcode,),
                    )
                    row = cur.fetchone()

            if not row:
                logger.warning(f"QR code introuvable (id={id_qrcode}).")
                return None

            # Support tuple ou dict
            if not isinstance(row, dict):
                # Convertit tuple en dict si nécessaire (au cas où le curseur n’est pas RealDictCursor)
                colnames = [desc[0] for desc in cur.description]
                row = dict(zip(colnames, row))

            return Qrcode(
                id_qrcode=row["id_qrcode"],
                url=row["url"],
                id_proprietaire=str(row["id_proprietaire"]),
                date_creation=row["date_creation"],
                type=row["type_qrcode"],
                couleur=row["couleur"],
                logo=row["logo"],
            )

        except Exception as e:
            logger.exception(f"Erreur lors de la recherche du QR code {id_qrcode} : {e}")
            return None

    def lister_par_proprietaire(self, id_user: int) -> List[Qrcode]:
        """
        Liste les QR codes d’un propriétaire, triés par date_creation DESC.
        """
        try:
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id_qrcode, url, id_proprietaire, date_creation, type_qrcode, couleur, logo
                        FROM qrcode
                        WHERE id_proprietaire = %s
                        ORDER BY date_creation DESC;
                        """,
                        (id_user,),
                    )
                    rows = cur.fetchall()

            qrcodes = []
            for r in rows:
                if not isinstance(r, dict):
                    # Convertir tuple en dict si nécessaire
                    colnames = [desc[0] for desc in cur.description]
                    r = dict(zip(colnames, r))
                qrcodes.append(
                    Qrcode(
                        id_qrcode=r["id_qrcode"],
                        url=r["url"],
                        id_proprietaire=str(r["id_proprietaire"]),
                        date_creation=r["date_creation"],
                        type=r["type_qrcode"],
                        couleur=r["couleur"],
                        logo=r["logo"],
                    )
                )
            logger.info(f"{len(qrcodes)} QR codes récupérés pour l’utilisateur {id_user}.")
            return qrcodes

        except Exception as e:
            logger.exception(f"Erreur lors du listing des QR codes pour user {id_user} : {e}")
            return []

    def mettre_a_jour(
        self,
        id_qrcode: int,
        id_user: int,
        url: Optional[str] = None,
        type_qrcode: Optional[bool] = None,
        couleur: Optional[str] = None,
        logo: Optional[str] = None,
    ) -> Optional[Qrcode]:
        """
        Met à jour les champs fournis et retourne l’objet mis à jour,
        ou None si id introuvable ou accès non autorisé.
        """
        try:
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    # Vérifie le propriétaire
                    cur.execute(
                        "SELECT id_proprietaire FROM qrcode WHERE id_qrcode = %s;",
                        (id_qrcode,),
                    )
                    row = cur.fetchone()
                    if not row:
                        raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")
                    owner_id = row["id_proprietaire"] if isinstance(row, dict) else row[0]
                    if owner_id != id_user:
                        raise UnauthorizedError("Vous ne pouvez modifier que vos propres QR codes.")

                    # Mise à jour
                    cur.execute(
                        """
                        UPDATE qrcode
                        SET url = COALESCE(%s, url),
                            type_qrcode = COALESCE(%s, type_qrcode),
                            couleur = COALESCE(%s, couleur),
                            logo = COALESCE(%s, logo)
                        WHERE id_qrcode = %s
                        RETURNING id_qrcode, url, id_proprietaire, date_creation, type_qrcode, couleur, logo;
                        """,
                        (url, type_qrcode, couleur, logo, id_qrcode),
                    )
                    updated = cur.fetchone()
                conn.commit()

            if not updated:
                raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable après mise à jour.")

            # Support tuple ou dict
            if not isinstance(updated, dict):
                colnames = [desc[0] for desc in cur.description]
                updated = dict(zip(colnames, updated))

            logger.info(f"QR code {id_qrcode} mis à jour avec succès par user {id_user}.")
            return Qrcode(
                id_qrcode=updated["id_qrcode"],
                url=updated["url"],
                id_proprietaire=str(updated["id_proprietaire"]),
                date_creation=updated["date_creation"],
                type=updated["type_qrcode"],
                couleur=updated["couleur"],
                logo=updated["logo"],
            )

        except UnauthorizedError as e:
            logger.warning(str(e))
            raise
        except QRCodeNotFoundError as e:
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.exception(f"Erreur lors de la mise à jour du QR code {id_qrcode} : {e}")
            return None
