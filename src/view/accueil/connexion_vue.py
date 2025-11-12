# src/view/connexion/connexion_vue.py
from InquirerPy import inquirer
import requests # AJOUT
import os       # AJOUT
import json     # AJOUT

from view.vue_abstraite import VueAbstraite
from view.session import Session
from service.utilisateur_service import UtilisateurService

# AJOUT : Définir l'URL de l'API
API_BASE_URL = os.getenv("BASE_API_URL", "http://127.0.0.1:5000")


class ConnexionVue(VueAbstraite):
    """Vue de Connexion (saisie de nom utilisateur et mot de passe)"""

    def choisir_menu(self):
        # Saisie
        nom_user = inquirer.text(message="Entrez votre nom d'utilisateur : ").execute()
        mdp = inquirer.secret(message="Entrez votre mot de passe : ").execute()

        # Authentification via le service (local)
        user = UtilisateurService().se_connecter(nom_user, mdp)

        if user:
            # --- AJOUT : Authentification auprès de l'API pour obtenir un token ---
            api_token = None
            message_api = ""
            try:
                login_endpoint = f"{API_BASE_URL.rstrip('/')}/login"
                # L'API s'attend à des données de formulaire (pas JSON) pour /login
                payload = {
                    "username": nom_user,
                    "password": mdp
                }
                print(f"Connexion à l'API ({login_endpoint}) pour obtenir un token...")
                response = requests.post(login_endpoint, data=payload, timeout=10)
                
                response.raise_for_status() # Lève une erreur si 4xx/5xx
                
                api_token = response.json().get("access_token")
                message_api = "Token API obtenu avec succès."
                
            except requests.exceptions.HTTPError as http_err:
                try:
                    detail = http_err.response.json().get('detail', http_err.response.text)
                except json.JSONDecodeError:
                    detail = http_err.response.text
                message = f"Erreur API lors du login: {http_err.response.status_code} - {detail}\nVérifiez que l'API est lancée et que vos identifiants sont corrects."
                from view.accueil.accueil_vue import AccueilVue
                return AccueilVue(message)
            except requests.exceptions.RequestException as req_err:
                message = f"Erreur de connexion à l'API: {req_err}\nVérifiez que l'API (app.py) est bien lancée sur {API_BASE_URL}."
                from view.accueil.accueil_vue import AccueilVue
                return AccueilVue(message)
            except Exception as e:
                message = f"Erreur inattendue lors de l'obtention du token : {e}"
                from view.accueil.accueil_vue import AccueilVue
                return AccueilVue(message)
            # --- FIN AJOUT ---

            # Message et session (MODIFIÉ)
            message = f"Vous êtes connecté en tant que {getattr(user, 'nom_user', nom_user)}\n{message_api}"
            Session().connexion(user, api_token) # MODIFIÉ : On passe le token

            # Navigation vers le menu utilisateur
            from view.menu_user_vue import MenuUtilisateurVue 
            return MenuUtilisateurVue(message)

        # Échec -> retour accueil avec message
        message = "Erreur de connexion (nom d'utilisateur ou mot de passe invalide)"
        from view.accueil.accueil_vue import AccueilVue
        return AccueilVue(message)