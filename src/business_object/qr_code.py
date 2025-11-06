from datetime import datetime, timezone
from typing import Optional


class Qrcode:
    """
    Classe métier représentant un QR code suivi.

    Utilisation des @property pour exposer un accès contrôlé aux attributs.
    - id_qrcode et date_creation sont en lecture seule (générés côté service/BDD).
    - url, type, couleur et logo sont modifiables via les setters avec validation.
    """

    def __init__(
        self,
        id_qrcode: Optional[int],
        url: str,
        id_proprietaire: str,
        date_creation: Optional[datetime] = None,
        type: bool = True,
        couleur: Optional[str] = None,
        logo: Optional[str] = None,
    ):
        """
        Args:
            id_qrcode: identifiant (peut être None si la BDD doit le générer).
            url: URL liée au QR code.
            id_proprietaire: identifiant du propriétaire (string).
            date_creation: datetime de création (None pour laisser la DB/Service la définir).
            type: True si QR suivi, False si QR simple.
            couleur: couleur optionnelle.
            logo: chemin/nom du logo optionnel.
        """
        self._id_qrcode = id_qrcode
        self._url = None
        self._id_proprietaire = id_proprietaire
        self._date_creation = date_creation or datetime.now(timezone.utc)
        self._type_qrcode = None
        self._couleur = None
        self._logo = None


        # Utiliser les setters pour valider les valeurs initiales
        self.url = url
        self.type = type
        if couleur is not None:
            self.couleur = couleur
        if logo is not None:
            self.logo = logo

    # -------------------
    # Propriétés (read-only / read-write)
    # -------------------

    @property
    def id_qrcode(self) -> Optional[int]:
        """Identifiant unique du QR code (lecture seule)."""
        return self._id_qrcode

    @property
    def url(self) -> str:
        """URL associée au QR code."""
        return self._url

    @url.setter
    def url(self, nouvelle_url: str) -> None:
        if not isinstance(nouvelle_url, str):
            raise TypeError("L'URL doit être une chaîne de caractères.")
        if not nouvelle_url.startswith(("http://", "https://")):
            raise ValueError("L'URL doit commencer par 'http://' ou 'https://'.")
        self._url = nouvelle_url

    @property
    def id_proprietaire(self) -> str:
        """Identifiant du propriétaire (lecture seule)."""
        return self._id_proprietaire

    @property
    def date_creation(self) -> datetime:
        """Date de création (lecture seule)."""
        return self._date_creation

    @property
    def type(self) -> bool:
        """Type du QR code (True = suivi, False = simple)."""
        return self._type

    @type.setter
    def type(self, t: bool) -> None:
        if not isinstance(t, bool):
            raise TypeError("Le champ 'type' doit être un booléen.")
        self._type = t

    @property
    def couleur(self) -> Optional[str]:
        """Couleur du QR code (optionnelle)."""
        return self._couleur

    @couleur.setter
    def couleur(self, c: str) -> None:
        if not isinstance(c, str):
            raise TypeError("La couleur doit être une chaîne de caractères.")
        self._couleur = c

    @property
    def logo(self) -> Optional[str]:
        """Logo associé au QR code (optionnel)."""
        return self._logo

    @logo.setter
    def logo(self, l: str) -> None:
        if not isinstance(l, str):
            raise TypeError("Le logo doit être une chaîne (chemin/nom).")
        self._logo = l

    def to_dict(self) -> dict:
        return {
        "id_qrcode": self.id_qrcode,
        "url": self.url,
        "id_proprietaire": self.id_proprietaire,
        "date_creation": self.date_creation.isoformat() if self.date_creation else None,
        "type": self.type,
        "couleur": self.couleur,
        "logo": self.logo,
        }

    def __repr__(self) -> str:
        return (
            f"Qrcode(id_qrcode={self._id_qrcode!r}, url={self._url!r}, "
            f"owner={self._id_proprietaire!r}, date_creation={self._date_creation!r})"
        )    

    




