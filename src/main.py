# main.py — Lanceur CLI (Accueil uniquement)
import logging
import dotenv

from utils.log_init import initialiser_logs
from view.accueil.accueil_vue import AccueilVue

if __name__ == "__main__":
    # Charger les variables d'environnement
    dotenv.load_dotenv(override=True)

    # Initialiser les logs
    initialiser_logs("Application")

    # Vue de départ
    vue_courante = AccueilVue("Bienvenue")
    nb_erreurs = 0

    # Boucle principale
    while vue_courante:
        if nb_erreurs > 100:
            print("Le programme recense trop d'erreurs et va s'arrêter")
            break
        try:
            # Afficher la vue courante
            vue_courante.afficher()

            # Basculer selon le choix de la vue
            vue_courante = vue_courante.choisir_menu()

        except Exception as e:
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





