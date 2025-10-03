from datetime import datetime

class Qrcode:
    def __init__(self, id_qrcode: int, url: str, id_proprietaire: str, 
                 date_creation: datetime, type: bool, couleur: str, logo: str):
        self.__id_qrcode = id_qrcode      # clé privée
        self.__url = url
        self.__id_proprietaire = id_proprietaire
        self.__date_creation = date_creation
        self.__type = type
        self.__couleur = couleur
        self.__logo = logo

    
    def afficher_infos(self):
        return f"QR {self.__id_qrcode} - {self.__url} ({self.__couleur})"

    # Getters
    def get_id(self):
        return self.__id_qrcode

    def get_url(self):
        return self.__url

    # Setters si nécessaire
    def set_url(self, nouvelle_url: str):
        self.__url = nouvelle_url
