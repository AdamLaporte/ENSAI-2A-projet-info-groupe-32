import regex
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator, PasswordValidator
from prompt_toolkit.validation import ValidationError, Validator

from service.utilisateur_service import UtilisateurService
from view.vue_abstraite import VueAbstraite


class InscriptionVue(VueAbstraite):
    def choisir_menu(self):
        # Demande à l'utilisateur de saisir nom, mot de passe...
        nom = inquirer.text(message="Entrez votre nom : ").execute()

        if UtilisateurService().nom_user_deja_utilise(nom):
            from view.accueil.accueil_vue import AccueilVue

            return AccueilVue(f"Le nom {nom} est déjà utilisé.")

        mdp = inquirer.secret(
            message="Entrez votre mot de passe : ",
            validate=PasswordValidator(
                length=5,
                cap=False,
                number=False,
                message="Au moins 5 caractères, incluant une majuscule et un chiffre",
            ),
        ).execute()




        # Appel du service pour créer le user
        user = UtilisateurService().creer_user(nom, mdp)

        # Si le user a été créé
        if user:
            message = (
                f"Votre compte {user.nom_user} a été créé. Vous pouvez maintenant vous connecter."
            )
        else:
            message = "Erreur de connexion (nom ou mot de passe invalide)"

        from view.accueil.accueil_vue import AccueilVue

        return AccueilVue(message)
