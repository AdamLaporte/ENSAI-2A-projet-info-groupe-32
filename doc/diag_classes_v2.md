classDiagram
    %% Entités
    class Utilisateur {
        +id_user: int
        +pseudo: string
        +mdp_hash: string
    }

    class Qrcode {
        +id_qrcode: int
        +url: string
        +date_creation: Date
        +type: string
        +couleur: string
        +logo: string
    }

    class Statistique {
        +id_stat: int
        +nombre_vue: int
        +dates_vues: List[Date]
    }

    class Token {
        +id_user: int
        +token: string
    }

    %% DAO
    class UtilisateurDao {
        +creer(Utilisateur): bool
        +trouver_par_id(int): Utilisateur
        +supprimer(Utilisateur): bool
        +modifier(Utilisateur): Utilisateur 
        +trouver_par_pseudo(string): Utilisateur
    }

    class QrcodeDao {
        +creer(Qrcode): bool
        +trouver_par_id(int): Qrcode
        +trouver_par_utilisateur(int): List[Qrcode]
        +supprimer(Qrcode): bool
    }

    class StatistiqueDao {
        +creer(Statistique): bool
        +modifier(int): bool
        +afficher(int): List
    }

    class TokenDao {
        +creer(Token): bool
        +get_token_by_user(int): Token
    }

    %% Service
    class UtilisateurService {
        +creer_utilisateur(pseudo:string, mdp:string): Utilisateur
        +login(pseudo:string, mdp:string): Token
        +modifier(Utilisateur): Utilisateur
    }

    class QrcodeService {
        +creer_qr(url:string, proprietaire:Utilisateur, type:string, couleur:string, logo:string): Qrcode
        +get_qr_par_utilisateur(id_user:int): List[Qrcode]
        +supprimer_qr(Qrcode): bool
    }

    class StatistiqueService {
        +ajouter_vue(qr:Qrcode): bool
        +afficher_statistiques(qr:Qrcode): List
    }

    class TokenService {
        +creer_token(user:Utilisateur): Token
        +verifier_token(token:Token): bool
    }

    %% Relations
    UtilisateurService --> UtilisateurDao : utilise
    QrcodeService --> QrcodeDao : utilise
    StatistiqueService --> StatistiqueDao : utilise
    TokenService --> TokenDao : utilise

    Utilisateur "1" --> "*" Qrcode : possede
    Qrcode "1" --> "*" Statistique : genere
    Token "1" --> "1" Utilisateur : appartient
