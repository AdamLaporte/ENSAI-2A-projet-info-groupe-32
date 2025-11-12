import regex
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator, PasswordValidator
from prompt_toolkit.validation import ValidationError, Validator
import requests # AJOUT
import os       # AJOUT
import json     # AJOUT

# MODIFIÉ : Suppression de l'import du service local
# from service.utilisateur_service import UtilisateurService 
from view.vue_abstraite import VueAbstraite

# AJOUT : Définir l'URL de l'API
API_BASE_URL = os.getenv("BASE_API_URL", "http://127.0.0.1:5000")


class InscriptionVue(VueAbstraite):
    def choisir_menu(self):
        # Demande à l'utilisateur de saisir nom, mot de passe...
        nom = inquirer.text(message="Entrez votre nom d'utilisateur : ").execute()

        # MODIFIÉ : La vérification d'unicité est maintenant gérée par l'API
        # if UtilisateurService().nom_user_deja_utilise(nom): ... (supprimé)

        mdp = inquirer.secret(
            message="Entrez votre mot de passe : ",
            validate=PasswordValidator(
                length=5,
                cap=False,  # Note : Votre validateur local autorise les mdp simples
                number=False, # mais le service les hash
                message="Au moins 5 caractères requis",
            ),
        ).execute()

        # --- MODIFIÉ : Appel à l'API pour créer le compte ---
        message = ""
        try:
            register_endpoint = f"{API_BASE_URL.rstrip('/')}/register"
            payload = {
                "nom_user": nom,
                "mdp": mdp
            }
            
            print(f"Appel de l'API POST {register_endpoint} pour créer le compte...")
            
            response = requests.post(register_endpoint, json=payload, timeout=10)
            
            response.raise_for_status() # Lève une erreur si 4xx ou 5xx
            
            response_data = response.json()
            message = (
                f"Votre compte {response_data.get('nom_user', nom)} a été créé avec succès.\n"
                "Vous pouvez maintenant vous connecter."
            )

        except requests.exceptions.HTTPError as http_err:
            try:
                # Essayer de lire le message d'erreur de l'API (ex: "nom déjà utilisé")
                detail = http_err.response.json().get('detail', http_err.response.text)
            except json.JSONDecodeError:
                detail = http_err.response.text
            message = f"Erreur API lors de l'inscription: {http_err.response.status_code} - {detail}"
        
        except requests.exceptions.RequestException as req_err:
            message = f"Erreur de connexion à l'API: {req_err}\nVérifiez que l'API (app.py) est bien lancée sur {API_BASE_URL}."
        
        except Exception as e:
            message = f"Erreur inattendue lors de l'inscription : {e}"
        # --- FIN MODIFICATION ---


        from view.accueil.accueil_vue import AccueilVue
        return AccueilVue(message)