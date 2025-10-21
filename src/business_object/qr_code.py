from datetime import datetime


class Qrcode:
    """
    Classe métier représentant un QR code suivi dans l'application.

    Cette classe encapsule toutes les informations relatives à un QR code :
    son identifiant unique, son URL associée, le propriétaire qui l’a créé,
    la date de création, le type (suivi ou non), ainsi que ses éléments de personnalisation
    comme la couleur et le logo.

    Attributs privés :
        __id_qrcode (int): Identifiant unique du QR code (clé privée).
        __url (str): Lien associé au QR code.
        __id_proprietaire (str): Identifiant de l’utilisateur propriétaire du QR code.
        __date_creation (datetime): Date de création du QR code.
        __type_qrcode (bool): Indique si le QR code est de type suivi (True) ou simple (False).
        __couleur (str): Couleur dominante du QR code.
        __logo (str): Logo intégré au centre du QR code.

    Méthodes publiques :
        afficher_infos() -> str :
            Retourne une représentation textuelle simplifiée du QR code.
        get_id() -> int :
            Retourne l’identifiant du QR code.
        get_url() -> str :
            Retourne l’URL associée au QR code.
        set_url(nouvelle_url: str) -> None :
            Met à jour l’URL du QR code.
    """

    def __init__(
        self,
        id_qrcode: int,
        url: str,
        id_proprietaire: str,
        date_creation: datetime,
        type_qrcode: bool,
        couleur: str,
        logo: str,
    ):
        """
        Constructeur de la classe Qrcode.

        Args:
            id_qrcode (int): Identifiant unique du QR code.
            url (str): URL associée au QR code.
            id_proprietaire (str): Identifiant du propriétaire du QR code.
            date_creation (datetime): Date de création du QR code.
            type (bool): Type de QR code (True = suivi, False = simple).
            couleur (str): Couleur du QR code.
            logo (str): Logo associé au QR code.
        """
        self.__id_qrcode = id_qrcode
        self.__url = url
        self.__id_proprietaire = id_proprietaire
        self.__date_creation = date_creation
        self.__type_qrcode = type_qrcode
        self.__couleur = couleur
        self.__logo = logo

    def afficher_infos(self) -> str:
        """
        Retourne une chaîne de caractères contenant les principales informations du QR code.

        Returns:
            str: Informations sous forme 'QR <id> - <url> (<couleur>)'
        """
        return f"QR {self.__id_qrcode} - {self.__url} ({self.__couleur})"

    def get_id(self) -> int:
        """
        Getter de l'identifiant du QR code.

        Returns:
            int: Identifiant unique du QR code.
        """
        return self.__id_qrcode

    def get_url(self) -> str:
        """
        Getter de l'URL du QR code.

        Returns:
            str: URL actuellement associée au QR code.
        """
        return self.__url

    def set_url(self, nouvelle_url: str) -> None:
        """
        Setter permettant de modifier l’URL du QR code.

        Args:
            nouvelle_url (str): Nouvelle URL à associer au QR code.
        """
        self.__url = nouvelle_url
