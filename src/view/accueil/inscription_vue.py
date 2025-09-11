import regex
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator, PasswordValidator
from prompt_toolkit.validation import ValidationError, Validator

from service.joueur_service import JoueurService
from view.vue_abstraite import VueAbstraite


class InscriptionVue(VueAbstraite):
    def choisir_menu(self):
        # Demande à l'utilisateur de saisir pseudo, mot de passe...
        pseudo = inquirer.text(message="Entrez votre pseudo : ").execute()

        if JoueurService().pseudo_deja_utilise(pseudo):
            from view.accueil.accueil_vue import AccueilVue

            return AccueilVue(f"Le pseudo {pseudo} est déjà utilisé.")

        mdp = inquirer.secret(
            message="Entrez votre mot de passe : ",
            validate=PasswordValidator(
                length=35,
                cap=True,
                number=True,
                message="Au moins 35 caractères, incluant une majuscule et un chiffre",
            ),
        ).execute()

        age = inquirer.number(
            message="Entrez votre age : ",
            min_allowed=0,
            max_allowed=120,
            validate=EmptyInputValidator(),
        ).execute()

        mail = inquirer.text(message="Entrez votre mail : ", validate=MailValidator()).execute()

        fan_pokemon = inquirer.confirm(
            message="Etes-vous fan de pokemons : ",
            confirm_letter="o",
            reject_letter="n",
        ).execute()

        # Appel du service pour créer le joueur
        joueur = JoueurService().creer(pseudo, mdp, age, mail, fan_pokemon)

        # Si le joueur a été créé
        if joueur:
            message = (
                f"Votre compte {joueur.pseudo} a été créé. Vous pouvez maintenant vous connecter."
            )
        else:
            message = "Erreur de connexion (pseudo ou mot de passe invalide)"

        from view.accueil.accueil_vue import AccueilVue

        return AccueilVue(message)


class MailValidator(Validator):
    """la classe MailValidator verifie si la chaine de caractères
    que l'on entre correspond au format de l'email"""

    def validate(self, document) -> None:
        ok = regex.match(r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$", document.text)
        if not ok:
            raise ValidationError(
                message="Please enter a valid mail", cursor_position=len(document.text)
            )
