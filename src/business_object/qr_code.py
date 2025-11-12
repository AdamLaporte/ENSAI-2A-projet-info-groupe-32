from datetime import datetime, timezone
from typing import Optional


class Qrcode:
    """
        Représente un QR code (statique ou dynamique) généré par l'application.

        url : il s'agit d'un string encodé libre qui représente le contenu du qrcode qui peut être:
        - une URL,
        - un texte simple,
        - une instruction WiFi (WIFI:T:WPA;...),
        - des coordonnées GPS,
        - un identifiant interne,
        - une clé API,
        - etc.

        Autres attributs :
        id_qrcode : identifiant unique (généré par la BDD si None)
        id_proprietaire : id du propriétaire (str ou int)
        date_creation : datetime UTC (généré automatiquement si None)
        type_qrcode : bool (True = QR dynamique, False = statique)
        couleur : couleur optionnelle
        logo : chemin de logo optionnel
    
    """

    def __init__(
        self,
        id_qrcode: Optional[int],
        url: str,
        id_proprietaire: str,
        date_creation: Optional[datetime] = None,
        type_qrcode: bool = True,
        couleur: Optional[str] = None,
        logo: Optional[str] = None,
    ):
        # Attributs privés
        self.__id_qrcode = id_qrcode
        self.__id_proprietaire = id_proprietaire
        self.__date_creation = date_creation or datetime.now(timezone.utc)

        # Mise à None avant appel setter
        self.__url = None
        self.__type_qrcode = None
        self.__couleur = None
        self.__logo = None

        # Application des validations via setters
        self.url = url
        self.type_qrcode = type_qrcode

        if couleur is not None:
            self.couleur = couleur
        if logo is not None:
            self.logo = logo

    # ------------------------
    # GETTERS / SETTERS
    # ------------------------

    @property
    def id_qrcode(self) -> Optional[int]:
        return self.__id_qrcode

    @id_qrcode.setter
    def id_qrcode(self, value: int) -> None:
        """Autorisé, car le DAO doit pouvoir hydrater l'objet après INSERT."""
        self.__id_qrcode = value

    @property
    def url(self) -> str:
        return self.__url

    @url.setter
    def url(self, nouvelle_url: str) -> None:
        if not isinstance(nouvelle_url, str):
            raise TypeError("L'URL doit être une chaîne de caractères.")
        self.__url = nouvelle_url

    @property
    def id_proprietaire(self) -> str:
        return self.__id_proprietaire

    @id_proprietaire.setter
    def id_proprietaire(self, value: str) -> None:
        self.__id_proprietaire = value

    @property
    def date_creation(self) -> datetime:
        return self.__date_creation

    @date_creation.setter
    def date_creation(self, d: datetime) -> None:
        self.__date_creation = d

    @property
    def type_qrcode(self) -> bool:
        return self.__type_qrcode

    @type_qrcode.setter
    def type_qrcode(self, t: bool) -> None:
        if not isinstance(t, bool):
            raise TypeError("Le champ 'type_qrcode' doit être un booléen.")
        self.__type_qrcode = t

    @property
    def couleur(self) -> Optional[str]:
        return self.__couleur

    @couleur.setter
    def couleur(self, c: str) -> None:
        if not isinstance(c, str):
            raise TypeError("La couleur doit être une chaîne de caractères.")
        self.__couleur = c

    @property
    def logo(self) -> Optional[str]:
        return self.__logo

    @logo.setter
    def logo(self, l: str) -> None:
        if not isinstance(l, str):
            raise TypeError("Le logo doit être une chaîne (chemin/nom).")
        self.__logo = l

    # ------------------------
    # UTILITAIRES
    # ------------------------

    def to_dict(self) -> dict:
        return {
            "id_qrcode": self.id_qrcode,
            "url": self.url,
            "id_proprietaire": self.id_proprietaire,
            "date_creation": (
                self.date_creation.isoformat()
                if self.date_creation else None
            ),
            "type_qrcode": self.type_qrcode,
            "couleur": self.couleur,
            "logo": self.logo,
        }

    def __repr__(self) -> str:
        return (
            f"Qrcode(id_qrcode={self.__id_qrcode!r}, url={self.__url!r}, "
            f"owner={self.__id_proprietaire!r}, date_creation={self.__date_creation!r})"
        )
