@startuml

/' 
-------------------------------------------------------------------
  NOTICE D’UTILISATION DANS VSCODE 

  1. Installer Java et Graphviz dans l' environnement :
     - Ouvre un terminal puis tape :
         sudo apt update
         sudo apt install -y default-jre graphviz

  2. Dans VSCode :
     - Installer l’extension "PlantUML"

  3. Exécution :
     - Ouvrir ce fichier .puml dans VSCode
     - Appuyer sur ALT + D pour générer et prévisualiser le diagramme
------------------------------------------------------------------- 
'/


class Utilisateur {
    +id_user: int
    +nom_user: str 
    +mdp: str
}

class UtilisateurService {
    +creer_user(id_user : str, mdp : str): Utilisateur 
    +se_connecter(id_user : str, mdp : str): Utilisateur
    +modifier_user(id_user : str, mdp : str): Utilisateur
    +supprimer_user(id_user : str, mdp : str): bool   
}

class UtilisateurDao {
    +creer_user(id_user : str, mdp : str): bool
    +modifier_user(id_user : str, mdp : str): Utilisateur 
    +supprimer_user(id_user : str, mdp : str): bool
    +trouver_par_id_user(id_user : str): Utilisateur    
}

class Token {
    +id_user: str
    +id_token: int
    +jeton:str
    +date_expiration: datetime

}

class TokenService {
    +creer_token(id_user : str): Token
    +existe_token(id_user : str): str
    +est_valide_token(id_user : str, token : str): bool
    +trouver_id_user_par_token(token : str): str 
}

class TokenDao {
    +creer_token(id_user : str): Token
    +existe_token(id_user : str): str
    +est_valide_token(token : str): bool
    +trouver_id_user_par_token(token : str): str 
    +trouver_token_par_id_user(id_user : str): str 
    +trouver_token_par_valeur(token : str): bool
}

class QRCode {
    +id_qrcode: int
    +url: str
    +id_proprietaire: str
    +date_creation: date
    +type: bool
    +couleur: str
    +logo: str
}

class QRCodeService {
    +creer_qrc(url : str, type: bool, couleur : str, logo : str): QRCode
    +trouver_qrc_par_id_user(id_user : str): list[QRCode]
    +supprimer_qrc(id_qrcode, id_user): bool
    +verifier_proprietaire(QRCode, id_user: str): bool
    +trouver_qrc_par_id_qrc(id_qrcode : int): QRCode | None
}

class QRCodeDao {
    +creer_qrc(QRCode): QRCode
    +trouver_qrc_par_id(id_user: str): list[QRCode]
    +supprimer(id_qrcode): bool
    +modifier(QRCode): QRCode
}

' -------- LOG SCAN ------------
class LogScan {
    -id_scan: int
    -id_qrcode: int
    -date_scan: datetime
    -client_host: str
    -user_agent: str
    -referer: str
    -accept_language: str
    -geo_country: str
    -geo_region: str
    -geo_city: str
}

class LogScanService {
    +creer_logscan(LogScan): LogScan
    +trouver_logs_par_qrcode(id_qrcode : int): list[LogScan]
}

class LogScanDao {
    +creer_logscan(LogScan): bool
    +trouver_logs_par_qrcode(id_qrcode : int): list[LogScan]
}

' -------- STATISTIQUE DERIVÉE ------------
class Statistique {
    -id_qrcode: int
    -id_stat: int
    -nombre_vue: int
    -date_des_vues: list[date]
}

class StatistiqueService {
    +afficher(id_qrcode : int, token : str): list[list]
    +creer_Statistique(id_qrcode : int): Statistique
    +modifier_Statistique(id_qrcode : int): bool
}

class StatistiqueDao {
    +creer_Statistique(Statistique): bool
    +modifier_Statistique(id_qrcode: int): bool
    +afficher(id_qrcode : int): list[list]
}

' ------------ RELATIONS ----------------

UtilisateurService --> UtilisateurDao 
UtilisateurService ..> Utilisateur

TokenService --> TokenDao   
TokenService ..> Token
TokenService -- UtilisateurService

QRCodeService --> QRCodeDao 
QRCodeService ..> QRCode
QRCodeService -- UtilisateurService
QRCodeService -- LogScanService

LogScanService --> LogScanDao
LogScanService ..> LogScan

' Statistique dépend de LogScan pour calculer les vues
StatistiqueService --> LogScanDao
StatistiqueService ..> LogScan
StatistiqueService --> StatistiqueDao
StatistiqueService ..> Statistique

@enduml
