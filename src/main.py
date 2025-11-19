"""
Lanceur principal de l'application en ligne de commande (CLI).

Ce module initialise l'environnement, le système de logs et démarre la boucle 
principale de navigation entre les différentes vues (menus) de l'application.
"""
import logging
import dotenv

from utils.log_init import initialiser_logs
from view.accueil.accueil_vue import AccueilVue

if __name__ == "__main__":
    """
    Point d'entrée principal. 
    
    Orchestre le démarrage de l'application, gère la navigation dans les menus
    et assure une gestion des erreurs pour maintenir la boucle active.
    """
    # Charger les variables d'environnement (BASE_URL, DB config, etc.)
    dotenv.load_dotenv(override=True)

    # Initialiser les logs
    initialiser_logs("Application")

    # Démarrer la première vue
    vue_courante = AccueilVue("Bienvenue")
    nb_erreurs = 0

    # Boucle principale de navigation entre les vues (menus)
    while vue_courante:
        if nb_erreurs > 100:
            print("Le programme recense trop d'erreurs et va s'arrêter")
            break
        try:
            # 1. Afficher la vue actuelle (nettoie la console et affiche le message)
            vue_courante.afficher()

            # 2. Obtenir la vue suivante en fonction du choix de l'utilisateur
            vue_courante = vue_courante.choisir_menu()

        except Exception as e:
            # Gestion basique des erreurs : journalise l'exception et retourne au menu d'accueil
            logging.error(f"{type(e).__name__} : {e}", exc_info=True)
            nb_erreurs += 1
            vue_courante = AccueilVue(
                "Une erreur est survenue, retour au menu principal.\n"
                "Consultez les logs pour plus d'informations."
            )

    # Fin de l'application
    print("----------------------------------")
    print("Au revoir")
    logging.info("Fin de l'application")