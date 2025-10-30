# src/view/connexion/connexion_vue.py
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from service.utilisateur_service import UtilisateurService

class ConnexionVue(VueAbstraite):
    """Vue de Connexion (saisie de nom utilisateur et mot de passe)"""

    def choisir_menu(self):
        # Saisie
        nom_user = inquirer.text(message="Entrez votre nom d'utilisateur : ").execute()
        mdp = inquirer.secret(message="Entrez votre mot de passe : ").execute()

        # Authentification via le service
        user = UtilisateurService().se_connecter(nom_user, mdp)

        if user:
            # Message et session
            message = f"Vous êtes connecté en tant que {getattr(user, 'nom_user', nom_user)}"
            Session().connexion(user)

            # Navigation vers le menu utilisateur
            from view.menu_user_vue import MenuUtilisateurVue 
            return MenuUtilisateurVue(message)

        # Échec -> retour accueil avec message
        message = "Erreur de connexion (nom d'utilisateur ou mot de passe invalide)"
        from view.accueil.accueil_vue import AccueilVue
        return AccueilVue(message)
