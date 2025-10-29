
# Diagramme de classes des objets métiers

Ce diagramme est codé avec [mermaid](https://mermaid.js.org/syntax/classDiagram.html) :

* avantage : facile à coder
* inconvénient : on ne maîtrise pas bien l'affichage

Pour afficher ce diagramme dans VScode :

* à gauche aller dans **Extensions** (ou CTRL + SHIFT + X)
* rechercher `mermaid`
  * installer l'extension **Markdown Preview Mermaid Support**
* revenir sur ce fichier
  * faire **CTRL + K**, puis **V**

``` mermaid 

classDiagram
    class Utilisateur {
        +id_user: str 
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
        +token: str
    }

    class TokenService {
        +creer_token(id_user : str): Token
        +existe_token(id_user : str): token : str 
        +est_valide_token(id_user : str, token : str): bool
        +trouver_id_user_par_token(token : str): id_user : str 
    }

    class TokenDao {
        +creer_token(id_user : str): Token
        +existe_token(id_user : str): token : str 
        +est_valide_token(token : str): bool
        +trouver_id_user_par_token(id_user : str, token : str): id_user : str 
        +trouver_token_par_id_user(id_user : str): token : str 
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
        +supprimer_qrc(QRCode): bool
        +verifier_proprietaire(QRCode, id_user: str): bool
        +trouver_qrc_par_id_qrc(id_user : str): Qrcode | None
    }

    class QRCodeDao {
        +creer_qrc(QRCode): QRCode
        +trouver_qrc_par_id(id_user: str): list[QRCode]
        +supprimer(QRCode): bool
        +modifier(QRCode):QRCode
    }
    

    class Statistique {
        +id_qrcode: int
        +id_stat : date
        +nombre_vue: str
        +date_des_vues: list[id_stat]
    }
    
    class StatistiqueService {
        +creer_Statistique(id_qrcode : int): Statistique
        +modifier_Statistique(id_qrcode : int): bool
        +afficher(id_qrcode : int, token : str): list[list]
    }

    class StatistiqueDao {
        +creer_Statistique(Statistique): bool
        +modifier_Statistique(id_qrcode: int): bool
        +afficher(id_qrcode : int): list[list]
    }
    

    UtilisateurService --> UtilisateurDao 
    UtilisateurService ..> Utilisateur: utilise

    StatistiqueService --> StatistiqueDao 
    StatistiqueService ..> Statistique: utilise

    QRCodeService --> QRCodeDao 
    QRCodeService ..> QRCode : utilise

    TokenService --> TokenDao   
    TokenService ..> Token : utilise

    TokenService -- UtilisateurService 
    StatistiqueService -- QRCodeService
    QRCodeService -- UtilisateurService

```