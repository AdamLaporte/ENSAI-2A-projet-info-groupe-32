import logging
from typing import List, Optional, Any, Dict

from utils.singleton import Singleton
from utils.log_decorator import log

from dao.db_connexion import DBConnection
from business_object.qr_code import Qrcode

logger = logging.getLogger(__name__)


class QRCodeNotFoundError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class QRCodeDao:
    """
    DAO simple pour la table `qrcodes`.
    Style : lecture via propriétés de Qrcode, méthodes d'écriture renvoyant bool,
    méthode de modification renvoyant l'objet mis à jour.
    """

    def __init__(self):
        # DBConnection fournit une connexion (RealDictCursor configuré)
        self._db = DBConnection()

    @log
    def creer_qrc(self, qrcode: Qrcode) -> bool:
        """
        Insère un QRCode en base. Retourne True si création réussie.
        (Si l'id est fourni dans qrcode.id_qrcode, on l'insère, sinon la DB le génèrera.)
        """
        try:
            with self._db.connection as conn:
                with conn.cursor() as cur:
                    if qrcode.id_qrcode is not None:
                        cur.execute(
                            """
                            INSERT INTO qrcodes (id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING id_qrcode;
                            """,
                            (
                                qrcode.id_qrcode,
                                qrcode.url,
                                qrcode.id_proprietaire,
                                qrcode.date_creation,
                                qrcode.type,
                                qrcode.couleur,
                                qrcode.logo,
                            ),
                        )
                    else:
                        cur.execute(
                            """
                            INSERT INTO qrcodes (url, id_proprietaire, type, couleur, logo)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING id_qrcode;
                            """,
                            (
                                qrcode.url,
                                qrcode.id_proprietaire,
                                qrcode.date_creation,
                                qrcode.type,
                                qrcode.couleur,
                                qrcode.logo,
                            ),
                        )
                    res = cur.fetchone()
                # commit pris en charge par le context manager ou explicitement selon impl
                # ici on suppose que `with connection` commit automatiquement si pas d'exception
            return bool(res)
        except Exception as e:
            logger.exception("Erreur lors de creer_qrc : %s", e)
            return False

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
    
    
    @log
    def trouver_qrc_par_id_qrc(self, id_qrcode: int) -> Qrcode | None:
        """
        Recherche un QR code à partir de son identifiant unique.

        Parameters
        ----------
        id_qrcode : int
        Identifiant du QR code à rechercher.

        Returns
        -------
        Qrcode | None
        L'objet Qrcode correspondant, ou None s'il n'existe pas.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo
                        FROM qrcodes
                        WHERE id_qrcode = %(id_qrcode)s;
                        """,
                        {"id_qrcode": id_qrcode},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(f"Erreur lors de la recherche du QR code {id_qrcode} : {e}")
            return None

        if res:
            return Qrcode(
                id_qrcode=res["id_qrcode"],
                url=res["url"],
                id_proprietaire=res["id_proprietaire"],
                date_creation=res["date_creation"],
                type=res.get("type"),
                couleur=res.get("couleur"),
                logo=res.get("logo"),
            )
        return None



    @log
    def modifier_qrc(
        self,
        id_qrcode: Any,
        id_user: str,
        url: Optional[str] = None,
        type_: Optional[bool] = None,
        couleur: Optional[str] = None,
        logo: Optional[str] = None,
    ) -> Qrcode:
        """
        Modifie un QR code après vérification du propriétaire.
        Retourne le Qrcode mis à jour ou lève QRCodeNotFoundError/UnauthorizedError.
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
                        raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable.")
                    if row["id_proprietaire"] != id_user:
                        raise UnauthorizedError("Seul le propriétaire peut modifier ce QR code.")

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
                raise QRCodeNotFoundError(f"QR code {id_qrcode} introuvable après tentative de mise à jour.")
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
                    cur.execute("DELETE FROM qrcodes WHERE id_qrcode = %s;", (qid,))
                    deleted = cur.rowcount > 0
            return bool(deleted)
        except Exception as e:
            logger.exception("Erreur lors de supprimer : %s", e)
            return False
