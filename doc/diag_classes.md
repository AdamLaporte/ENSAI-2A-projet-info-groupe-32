
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

```mermaid
classDiagram
    class Utilisateur {
        +id_user: int
        +pseudo: string
        +mdp: string
    }
    
    class UtilisateurDao {
        +creer(Utilisateur): bool
        +trouver_par_id(int): Utilisateur
        +supprimer(Utilisateur): bool
        +se_connecter(str,str): Utilisateur
    }
    
    class UtilisateurService {
        +creer(str, str): Utilisateur
        +trouver_par_id(int): Utilisateur
        +supprimer(Utilisateur): bool
        +se_connecter(str,str): Utilisateur
    }

    class Qrcode {
        +id_qrcode: int
        +url: str
        +id_propriétaire: int
        +date_création: date
        +type: bool
        +couleur: str
        +logo: str
    }
    
    class QrcodeDao {
        +creer_Qr(Qrcode): bool
        +trouver_Qr_par_id(int): list[Qrcode]
        +supprimer(Qrcode): bool
    }
    
    class QrcodeService {
        +creer_Qr(str, int, str, str): Qrcode
        +trouver_Qr_par_id(int): list[Qrcode]
        +supprimer(Qrcode): bool
    }

    class Statistique {
        +id_qrcode: int
        +nombre_vue: str
        +date_des_vues: list[date]
    }
    
    class StatistiqueDao {
        +creer_Statistique(Statistique): bool
        +modifier_Statistique(int): bool
        +afficher(int): list[list]

    }
    
    class StatistiqueService {
        +creer_Statistique(int): Statistique
        +modifier_Statistique(int): bool
        +afficher(int): list[list]
    }

    class VueAbstraite{
      +afficher()
      +choisir_menu()
    }


    UtilisateurService --|> UtilisateurDao : appelle
    UtilisateurService --|> Utilisateur: utilise

    StatistiqueService --|> StatistiqueDao : appelle
    StatistiqueService --|> Statistique: utilise

    QrcodeService --|> QrcodeDao : appelle
    QrcodeService --|> Qrcode : utilise



```
