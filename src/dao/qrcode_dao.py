# dao/qrcode_dao.py
from typing import List, Optional, Any, Dict
import logging

from dao.db_connexion import DBConnection
from business_object.qr_code import Qrcode

logger = logging.getLogger(__name__)


class QRCodeNotFoundError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class QRCodeDao:
    """
    DAO pour la table `qrcodes`.
    - Les méthodes retournent l'objet Qrcode reconstruit quand pertinent.
    - Elles gèrent proprement la transaction (commit/rollback) et lèvent des exceptions métier.
    - Compatible avec Qrcode exposant des @property (préféré) ou des getters get_*
    """

    def __init__(self):
        self.conn = DBConnection().connection  # RealDictCursor configuré dans DBConnection

    # --- utilitaire pour extraire un attribut depuis l'objet Qrcode ---
    def _get_attr_from_obj(self, obj: Any, attr: str):
        """
        Tente plusieurs stratégies pour récupérer une valeur depuis l'objet métier :
         1) propriété publique (ex: obj.id_qrcode)
         2) getter get_<attr>()
         3) attribut protégé _<attr>
         4) attribut name-mangled _ClassName__<attr>
        Retourne None si aucune valeur trouvée (ou si celle-ci est réellement None).
        """
        # 1) propriété / attribut direct
        if hasattr(obj, attr):
            return getattr(obj, attr)

        # 2) getter get_<attr>
        getter_name = f"get_{attr}"
        if hasattr(obj, getter_name) and callable(getattr(obj, getter_name)):
            return getattr(obj, getter_name)()

        # 3) attribut protégé conventionnel
        protected_name = f"_{attr}"
        if hasattr(obj, protected_name):
            return getattr(obj, protected_name)

        # 4) name-mangled (class name needed)
        cls_name = obj.__class__.__name__
        mangled = f"_{cls_name}__{attr}"
        if hasattr(obj, mangled):
            return getattr(obj, mangled)

        # nothing found
        return None

    # --- utilitaire pour construire un Qrcode depuis une ligne DB (dict) ---
    def _row_to_qrcode(self, row: Dict[str, Any]) -> Qrcode:
        return Qrcode(
            id_qrcode=row["id_qrcode"],
            url=row["url"],
            id_proprietaire=row["id_proprietaire"],
            date_creation=row["date_creation"],
            type=row.get("type"),
            couleur=row.get("couleur"),
            logo=row.get("logo"),
        )

    # --- CREATE : insert et renvoie l'objet créé (avec id) ---
    def creer_qrc(self, qrcode: Qrcode) -> Qrcode:
        """
        Insère un nouveau QRCode en base et renvoie l'objet persistant (avec id, date_creation).
        Si l'objet Qrcode a déjà un id (rare), on l'insère avec cet id ; sinon la DB génère l'id.
        """
        try:
            with self.conn.cursor() as cur:
                provided_id = self._get_attr_from_obj(qrcode, "id_qrcode")
                if provided_id is not None:
                    sql = """
                    INSERT INTO qrcodes (id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo
                    """
                    params = (
                        provided_id,
                        self._get_attr_from_obj(qrcode, "url"),
                        self._get_attr_from_obj(qrcode, "id_proprietaire"),
                        self._get_attr_from_obj(qrcode, "date_creation"),
                        self._get_attr_from_obj(qrcode, "type"),
                        self._get_attr_from_obj(qrcode, "couleur"),
                        self._get_attr_from_obj(qrcode, "logo"),
                    )
                else:
                    sql = """
                    INSERT INTO qrcodes (url, id_proprietaire, date_creation, type, couleur, logo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo
                    """
                    params = (
                        self._get_attr_from_obj(qrcode, "url"),
                        self._get_attr_from_obj(qrcode, "id_proprietaire"),
                        self._get_attr_from_obj(qrcode, "date_creation"),
                        self._get_attr_from_obj(qrcode, "type"),
                        self._get_attr_from_obj(qrcode, "couleur"),
                        self._get_attr_from_obj(qrcode, "logo"),
                    )

                cur.execute(sql, params)
                row = cur.fetchone()
            self.conn.commit()
            if not row:
                raise Exception("Insertion effectuée mais la base n'a pas renvoyé la ligne.")
            return self._row_to_qrcode(row)

        except Exception:
            logger.exception("Erreur lors de creer_qrc")
            try:
                self.conn.rollback()
            except Exception:
                logger.exception("Rollback a échoué dans creer_qrc")
            raise

    # --- FIND by owner (ancienne trouver_par_id) ---
    def trouver_par_id(self, id_user: str) -> List[Qrcode]:
        """
        Retourne la liste des QRCodes pour un propriétaire donné.
        (Nom ancien : trouver_par_id ; garde le nom pour compatibilité)
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo
                    FROM qrcodes
                    WHERE id_proprietaire = %s
                    ORDER BY date_creation DESC
                    """,
                    (id_user,),
                )
                rows = cur.fetchall()
            return [self._row_to_qrcode(row) for row in rows]
        except Exception:
            logger.exception("Erreur lors de trouver_par_id")
            raise

    # --- UPDATE (modification explicite) ---
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
        Modifie un QR code existant après vérification du propriétaire.
        Retourne l'objet Qrcode mis à jour.
        """
        try:
            with self.conn.cursor() as cur:
                # Vérifier existence et propriétaire
                cur.execute("SELECT id_proprietaire FROM qrcodes WHERE id_qrcode = %s", (id_qrcode,))
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
                    RETURNING id_qrcode, url, id_proprietaire, date_creation, type, couleur, logo
                    """,
                    (url, type_, couleur, logo, id_qrcode),
                )
                updated_row = cur.fetchone()

            self.conn.commit()
            if not updated_row:
                # Très improbable : existait lors du SELECT mais pas après
                raise QRCodeNotFoundError(
                    f"QR code {id_qrcode} introuvable après tentative de mise à jour."
                )
            return self._row_to_qrcode(updated_row)

        except (QRCodeNotFoundError, UnauthorizedError):
            try:
                self.conn.rollback()
            except Exception:
                logger.exception("Rollback a échoué dans modifier_qrc (handled exception)")
            raise
        except Exception:
            logger.exception("Erreur lors de modifier_qrc")
            try:
                self.conn.rollback()
            except Exception:
                logger.exception("Rollback a échoué dans modifier_qrc")
            raise

    # --- DELETE ---
    def supprimer(self, qrcode: Qrcode) -> bool:
        """
        Supprime le QRCode donné (par id retourné par qrcode.id_qrcode ou get_id()).
        Retourne True si une ligne a été effacée.
        """
        try:
            # on récupère l'id en tolérant plusieurs API d'objet
            qid = self._get_attr_from_obj(qrcode, "id_qrcode")
            if qid is None:
                raise ValueError("Impossible de récupérer l'identifiant du Qrcode fourni.")
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM qrcodes WHERE id_qrcode = %s", (qid,))
                deleted = cur.rowcount > 0
            self.conn.commit()
            return bool(deleted)
        except Exception:
            logger.exception("Erreur lors de supprimer")
            try:
                self.conn.rollback()
            except Exception:
                logger.exception("Rollback a échoué dans supprimer")
            raise
