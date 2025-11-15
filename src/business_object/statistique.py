from datetime import date, datetime

class Statistique:
    """
    Classe représentant les Statistiques.

    Attributs 
    ------------------
   id_qrcode : int
        Identifiant du QR code.
    id_stat : int
        Identifiant interne de la ligne statistique.
    nombre_vue : int
        Nombre de vues du QR code pour une date donnée.
    date_des_vues : list[date]
        Liste des dates correspondant aux vues enregistrées.
    """

    def __init__(self, id_qrcode=None, id_stat=None, nombre_vue=None, date_des_vues=None):
        """Constructeur avec validation."""

        if id_qrcode is not None and not isinstance(id_qrcode, int):
            raise ValueError("L'identifiant du qrcode doit être un entier")
        if id_stat is not None and not isinstance(id_stat, int):
            raise ValueError("L'identifiant de la statistique doit être un entier")
        if nombre_vue is not None and not isinstance(nombre_vue, int):
            raise ValueError("Le nombre de vues doit être entier")
        if date_des_vues is not None:
            if not isinstance(date_des_vues, list):
                raise ValueError("Les dates doivent être stockées dans une liste")
            for elt in date_des_vues:
                if not isinstance(elt, (date, datetime)):
                    raise ValueError("La liste doit contenir des objets date ou datetime")

        # --- Attributs privés ---
        self.__id_qrcode = id_qrcode
        self.__id_stat = id_stat
        self.__nombre_vue = nombre_vue
        self.__date_des_vues = date_des_vues

    # ----------------------------
    # Getters / Setters
    # ----------------------------

    @property
    def id_qrcode(self):
        return self.__id_qrcode

    @id_qrcode.setter
    def id_qrcode(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("L'identifiant du qrcode doit être un entier")
        self.__id_qrcode = value

    @property
    def id_stat(self):
        return self.__id_stat

    @id_stat.setter
    def id_stat(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("L'identifiant de la statistique doit être entier")
        self.__id_stat = value

    @property
    def nombre_vue(self):
        return self.__nombre_vue

    @nombre_vue.setter
    def nombre_vue(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("Le nombre de vues doit être entier")
        self.__nombre_vue = value

    @property
    def date_des_vues(self):
        return self.__date_des_vues

    @date_des_vues.setter
    def date_des_vues(self, value):
        if value is not None and not isinstance(value, list):
            raise ValueError("Les dates des vues doivent être stockées dans une liste")

        for d in value:
            if not isinstance(d, (date, datetime)):
                raise ValueError("Chaque élément doit être un objet date ou datetime")

        self.__date_des_vues = value

    # ----------------------------
    # Représentation et comparaison
    # ----------------------------

    def __str__(self):
        """Affiche les informations principales de la statistique."""
        return (
            f"Statistique(QRCode={self.__id_qrcode}, "
            f"Vues={self.__nombre_vue}, Dates={self.__date_des_vues})"
        )

    def __eq__(self, other):
        """Deux statistiques sont égales si elles concernent le même QRCode."""
        if not isinstance(other, Statistique):
            return False
        return self.__id_qrcode == other.__id_qrcode
