from InquirerPy import inquirer
import os
import requests  # Ajout pour les requêtes HTTP
import json      # Ajout pour formater le payload

from view.vue_abstraite import VueAbstraite
from view.session import Session

# Ces imports ne sont plus nécessaires car la vue est entièrement pilotée par l'API
# from dao.qrcode_dao import QRCodeDao
# from service.qrcode_service import QRCodeService
# from dao.db_connection import DBConnection

# URL de base de l'API. Doit correspondre à votre .env
API_BASE_URL = os.getenv("BASE_API_URL", "http://127.0.0.1:5000")


class MenuUtilisateurVue(VueAbstraite):
    """Menu utilisateur: session, mes QR codes, stats de mes QR, création, déconnexion"""

    def _get_current_user(self):
        # Centralise la récupération de l'utilisateur depuis la Session
        sess = Session()
        return getattr(sess, "user", None) or getattr(sess, "joueur", None) or getattr(sess, "utilisateur", None)

    def _build_scan_url(self, qr_id: int) -> str:
        """
        Construit l'URL de scan à afficher dans le terminal.
        """
        scan_base = os.getenv("SCAN_BASE_URL")
        if not scan_base:
            print("AVERTISSEMENT: SCAN_BASE_URL n'est pas défini dans .env")
            return f"URL_SCAN_NON_DEFINIE/{qr_id}"
        
        base = scan_base.rstrip("/")
        return f"{base}/{qr_id}"

    # --- HELPER POUR FORMATER LA DATE ---
    def _format_date(self, iso_string):
        if not iso_string: return 'N/A'
        try: return iso_string.split('T')[0]
        except Exception: return iso_string


    def choisir_menu(self):
        print("\n" + "-" * 50 + "\nMenu Utilisateur\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Infos de session",
                "Lister mes QR codes (via API)",
                "Voir statistiques d'un de MES QR (via API)", 
                "Créer un QR code (via API)",
                "Se déconnecter",
            ],
        ).execute()

        match choix:
            case "Se déconnecter":
                Session().deconnexion()
                from view.accueil.accueil_vue import AccueilVue
                return AccueilVue()

            case "Infos de session":
                return MenuUtilisateurVue(Session().afficher())

            case "Lister mes QR codes (via API)":
                try:
                    # 1. Récupérer l'utilisateur
                    user = self._get_current_user()
                    if user is None:
                        return MenuUtilisateurVue("Non connecté.")
                    
                    id_user = getattr(user, "id_user", None)
                    nom_user = getattr(user, 'nom_user', id_user) # Pour l'en-tête
                    
                    if not id_user:
                        return MenuUtilisateurVue("Impossible de déterminer l'id utilisateur.")

                    # 2. Construire l'URL de l'API et appeler
                    api_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/utilisateur/{str(id_user)}"
                    print(f"Appel de l'API GET {api_endpoint}...")

                    response = requests.get(api_endpoint, timeout=10)
                    response.raise_for_status()  # Lève une erreur si statut 4xx ou 5xx

                    qrs_data = response.json()
                    if not qrs_data:
                        return MenuUtilisateurVue(f"Aucun QR code trouvé pour {nom_user} via l'API.")

                    # --- NOUVELLE LOGIQUE DE FILTRAGE ---
                    print("\nFiltrer la liste de vos QR codes :")
                    filter_choice = inquirer.select(
                        message="Afficher :",
                        choices=["Tous", "Uniquement les QR suivis", "Uniquement les QR non-suivis"],
                        default="Tous",
                    ).execute()

                    filtered_list = []
                    if filter_choice == "Tous":
                        filtered_list = qrs_data
                    elif filter_choice == "Uniquement les QR suivis":
                        # --- MODIFIÉ ---
                        filtered_list = [q for q in qrs_data if q.get("type") is True]
                    else: # "Uniquement les QR non-suivis"
                        # --- MODIFIÉ ---
                        filtered_list = [q for q in qrs_data if q.get("type") is False]

                    if not filtered_list:
                        return MenuUtilisateurVue("Aucun QR code ne correspond à ce filtre.")

                    # --- NOUVELLE LOGIQUE DE SÉLECTION ---
                    print("\nSélectionnez un QR code pour voir les détails :")
                    options = []
                    for q in filtered_list:
                        # --- MODIFIÉ ---
                        suivi_str = "(Suivi)" if q.get("type") is True else "(Non-suivi)"
                        options.append(f"#{q.get('id_qrcode', '?')} {suivi_str} → {q.get('url', 'N/A')}")
                    
                    selection = inquirer.select(
                        message="Vos QR codes filtrés :",
                        choices=options,
                    ).execute()
                    
                    try:
                        # Extraire l'ID de la sélection (ex: "#123 ...")
                        id_qr_str = selection.split(' ')[0].lstrip("#")
                        id_qr = int(id_qr_str)
                    except Exception:
                        return MenuUtilisateurVue("Sélection invalide.")

                    # Retrouver l'objet complet du QR code sélectionné
                    selected_qr = next((q for q in filtered_list if q.get("id_qrcode") == id_qr), None)
                    
                    if not selected_qr:
                         return MenuUtilisateurVue(f"Erreur: impossible de retrouver les détails du QR #{id_qr}.")

                    # --- NOUVEL AFFICHAGE DES DÉTAILS ---
                    titre = f"Détails du QR code #{id_qr}"
                    lignes = ["\n" + titre, "-" * len(titre)]
                    lignes.append(f"URL de destination: {selected_qr.get('url', 'N/A')}")
                    lignes.append(f"Date de création:   {self._format_date(selected_qr.get('date_creation'))}")
                    
                    # --- MODIFIÉ ---
                    if selected_qr.get("type") is True:
                        lignes.append(f"Type:               Suivi (Dynamique)")
                        lignes.append(f"URL de scan (encodée): {selected_qr.get('scan_url', 'N/A')}")
                        lignes.append(f"URL de l'image:     {selected_qr.get('image_url', 'N/A')}")
                        lignes.append("Statistiques:       Disponibles (via le menu 'Voir statistiques')")
                    else:
                        lignes.append(f"Type:               Non-suivi (Classique)")
                        lignes.append(f"URL de scan (encodée): N/A (l'URL de destination est encodée directement)")
                        lignes.append(f"URL de l'image:     {selected_qr.get('image_url', 'N/A')}")
                        lignes.append("Statistiques:       Non disponibles")

                    lignes.append(f"Couleur:            {selected_qr.get('couleur', 'N/A')}")
                    lignes.append(f"Logo:               {selected_qr.get('logo') or 'aucun'}")
                    
                    return MenuUtilisateurVue("\n".join(lignes))

                except requests.exceptions.HTTPError as http_err:
                    # Gérer les erreurs de l'API (ex: 404, 500)
                    try:
                        detail = http_err.response.json().get('detail', http_err)
                    except json.JSONDecodeError:
                        detail = http_err.response.text
                    return MenuUtilisateurVue(f"Erreur API: {http_err.response.status_code} - {detail}")
                except requests.exceptions.RequestException as req_err:
                    # Gérer les erreurs de connexion
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur inattendue : {e}")


            case "Voir statistiques d'un de MES QR (via API)":
                try:
                    # 1) Utilisateur connecté
                    user = self._get_current_user()
                    if user is None:
                        return MenuUtilisateurVue("Non connecté.")
                    id_user = getattr(user, "id_user", None)
                    if not id_user:
                        return MenuUtilisateurVue("Impossible de déterminer l'id utilisateur.")

                    # 2) Lister uniquement MES QR (via API) et proposer un choix
                    list_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/utilisateur/{str(id_user)}"
                    print(f"Appel de l'API GET {list_endpoint} pour lister vos QRs...")
                    list_response = requests.get(list_endpoint, timeout=10)
                    list_response.raise_for_status()
                    
                    mes_qr_data = list_response.json()
                    
                    # --- MODIFIÉ : Filtrer pour ne montrer que les QR suivis ---
                    # --- MODIFIÉ ---
                    qr_suivis = [q for q in mes_qr_data if q.get("type") is True]
                    
                    if not qr_suivis:
                        return MenuUtilisateurVue("Vous n'avez aucun QR code 'suivi' pour lequel voir des stats.")

                    # Construit les options pour InquirerPy
                    options = [f"#{q.get('id_qrcode', '?')} {q.get('url', '')}" for q in qr_suivis]
                    selection = inquirer.select(
                        message="Choisissez un QR code 'suivi' :",
                        choices=options,
                    ).execute()

                    try:
                        id_qr = int(selection.split()[0].lstrip("#"))
                    except Exception:
                        return MenuUtilisateuVue("Sélection invalide.")

                    # 3) Récupérer les stats pour CET id (via API)
                    stats_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/{id_qr}/stats"
                    print(f"Appel de l'API GET {stats_endpoint}...")
                    stats_response = requests.get(stats_endpoint, timeout=10)
                    stats_response.raise_for_status()
                    
                    stats_data = stats_response.json() # Le dict de l'API

                    # 4) Construire l'URL de scan (helper)
                    scan_url = self._build_scan_url(id_qr)

                    # 5) Formater la sortie exactement comme demandé
                    titre = f"Statistiques de votre QR #{id_qr}"
                    lignes = [titre, "-" * len(titre)]
                    lignes.append(f"URL de scan API: {scan_url}")
                    
                    lignes.append(f"Total vues: {stats_data.get('total_vues', 0)}")
                    lignes.append(f"Première vue: {self._format_date(stats_data.get('premiere_vue'))}")
                    lignes.append(f"Dernière vue: {self._format_date(stats_data.get('derniere_vue'))}")
                    
                    par_jour = stats_data.get("par_jour", [])
                    if par_jour:
                        lignes.append("Détail par jour:")
                        for r in par_jour: # r est un dict {"date": "...", "vues": ...}
                            d = self._format_date(r.get("date"))
                            v = r.get("vues", 0)
                            lignes.append(f"- {d}: {v}")
                    else:
                        lignes.append("Détail par jour: Aucune vue enregistrée.")

                    return MenuUtilisateurVue("\n".join(lignes))
                
                except requests.exceptions.HTTPError as http_err:
                    try:
                        detail = http_err.response.json().get('detail', http_err)
                    except json.JSONDecodeError:
                        detail = http_err.response.text
                    # Gestion spéciale pour l'erreur 404 des stats
                    if http_err.response.status_code == 404:
                         return MenuUtilisateurVue(f"Info: {detail}")
                    return MenuUtilisateurVue(f"Erreur API: {http_err.response.status_code} - {detail}")
                except requests.exceptions.RequestException as req_err:
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur lors de la récupération des statistiques: {e}")


            case "Créer un QR code (via API)":
                try:
                    # 1. Récupérer l'utilisateur
                    user = self._get_current_user()
                    if user is None:
                        return MenuUtilisateurVue("Non connecté.")
                    id_user = getattr(user, "id_user", None)
                    if not id_user:
                        return MenuUtilisateurVue("Impossible de déterminer l'id utilisateur.")

                    # 2. Demander les infos
                    url = inquirer.text(message="URL cible du QR : ").execute().strip()
                    if not url:
                        return MenuUtilisateurVue("URL vide, opération annulée.")

                    # --- AJOUTÉ : Demander si le suivi est activé ---
                    is_tracked = inquirer.confirm(
                        message="Activer le suivi (statistiques) pour ce QR code ?",
                        default=True,
                    ).execute()
                    # --- FIN DE L'AJOUT ---

                    couleurs = ["black", "blue", "red", "green", "purple", "teal", "orange", "gray"]
                    couleur = inquirer.select(
                        message="Couleur du QR : ",
                        choices=couleurs,
                        default="black",
                    ).execute()

                    logo = inquirer.text(message="Chemin du logo (optionnel, Enter pour passer) : ").execute().strip()
                    logo = logo if logo else None

                    # 3. Préparer l'appel API
                    api_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/"
                    payload = {
                        "url": url,
                        "id_proprietaire": str(id_user), # L'API attend l'ID en string
                        "type_qrcode": is_tracked, # --- AJOUTÉ : Envoyer le choix
                        "couleur": couleur,
                        "logo": logo
                    }

                    print(f"Appel de l'API POST {api_endpoint}...")

                    # 4. Appeler l'API
                    response = requests.post(api_endpoint, json=payload, timeout=10)

                    # 5. Gérer la réponse de l'API
                    response.raise_for_status()  # Lève une erreur si statut 4xx ou 5xx
                    
                    response_data = response.json()
                    
                    lignes = [
                        "QR code créé avec succès via l'API:",
                        f"- id: {response_data.get('id_qrcode')}",
                        f"- url finale (redirection): {response_data.get('url')}",
                        f"- url encodée (scan API): {response_data.get('scan_url', 'N/A (suivi désactivé)')}", # --- Modifié
                        f"- couleur: {response_data.get('couleur')}",
                        f"- logo: {response_data.get('logo') or 'aucun'}",
                        f"- image publique: {response_data.get('image_url')}",
                        f"\nL'image a été sauvegardée sur le serveur (dans {os.getenv('QRCODE_OUTPUT_DIR', 'static/qrcodes')})"
                    ]
                    return MenuUtilisateurVue("\n".join(lignes))
                
                except requests.exceptions.HTTPError as http_err:
                    # Essayer de lire le message d'erreur de l'API
                    try:
                        detail = http_err.response.json().get('detail', http_err)
                    except json.JSONDecodeError:
                        detail = http_err.response.text
                    return MenuUtilisateurVue(f"Erreur API: {http_err.response.status_code} - {detail}")
                except requests.exceptions.RequestException as req_err:
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur inattendue : {e}")

        # Par défaut on reste sur le menu
        return self

