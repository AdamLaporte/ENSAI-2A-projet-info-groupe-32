import logging

import dotenv

from utils.log_init import initialiser_logs
from view.accueil.accueil_vue import AccueilVue

if __name__ == "__main__":
    # On charge les variables d'envionnement
    dotenv.load_dotenv(override=True)

    initialiser_logs("Application")

    vue_courante = AccueilVue("Bienvenue")
    nb_erreurs = 0

    while vue_courante:
        if nb_erreurs > 100:
            print("Le programme recense trop d'erreurs et va s'arrêter")
            break
        try:
            # Affichage du menu
            vue_courante.afficher()

            # Affichage des choix possibles
            vue_courante = vue_courante.choisir_menu()
        except Exception as e:
            logging.error(f"{type(e).__name__} : {e}", exc_info=True)
            nb_erreurs += 1
            vue_courante = AccueilVue(
                "Une erreur est survenue, retour au menu principal.\n"
                "Consultez les logs pour plus d'informations."
            )

    # Lorsque l on quitte l application
    print("----------------------------------")
    print("Au revoir")

    logging.info("Fin de l'application")
