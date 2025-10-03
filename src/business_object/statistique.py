
from datetime import date 

class Statistique:
    """
    Classe représentant les Statistiques 

    Attributs
    ----------
    _id_qrcode : int
        identifiant du qrcode (privé)
    _id_stat : int
        identifiant de la statistique (privé)
    _nombre_vue : int
        nombre de vue d'un qrcode (privé)
    _date_des_vues : list[date]
        dates auxquelles le qrcode a été vu (privé)
    """

    def __init__(self, id_qrcode=None, id_stat=None, nombre_vue=None, date_des_vues=None):
        """Constructeur avec validation"""
        if id_qrcode is not None and not isinstance(id_qrcode, int):
            raise ValueError("L'identifiant du qrcode doit être un entier")
        if id_stat is not None and not isinstance(id_stat, int):
            raise ValueError("L'identifiant de la statistique doit être un entier")
        if nombre_vue is not None and not isinstance(nombre_vue, int):
            raise ValueError("Le nombre de vues doit être entier")
        if date_des_vues is not None and not isinstance(date_des_vues, list):
            raise ValueError("Les dates doivent êtres stockées dans une liste")
            for elt in date_des_vues:
                if not isinstance(elt, date):
                    raise ValueError("La liste doit stocker des dates")        
        self._id_qrcode = id_qrcode
        self._id_stat = id_stat
        self._nombre_vue = nombre_vue
        self._date_des_vues = date_des_vues

    @property
    def id_qrcode(self):
        return self._id_qrcode
    
    @id_qrcode.setter
    def id_qrcode(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("L'identifiant du qrcode doit être un entier")
        self._id_qrcode = value
    
    @property
    def id_stat(self):
        return self._id_stat
    
    @id_stat.setter
    def id_stat(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("L'identifiant de la statistique doit être entier")
        self._id_stat = value

    @property
    def nombre_vue(self):
        return self._nombre_vue
    
    @nombre_vue.setter
    def nombre_vue(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("Le nombre de vues doit être entier")
        self._nombre_vue = value

    @property
    def date_des_vues(self):
        return self._date_des_vues
    
    @date_des_vues.setter
    def date_des_vues(self, value):
        if value is not None and not isinstance(value, list):
            raise ValueError("Les dates des vues doivent êtres stockées dans une liste")
        self._date_des_vues = value

#encore à faire : les élèments de date_des_vues + la suite

    def __str__(self):
        """Permet d'afficher les informations de l'utilisateur"""
        return f"Utilisateur({self._id_user})"
    
    def __eq__(self, other):
        if not isinstance(other, Statistique):
            return False
        return self._id_user == other._id_user
