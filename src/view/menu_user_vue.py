from InquirerPy import inquirer
import os
import requests  # Ajout pour les requêtes HTTP
import json      # Ajout pour formater le payload

from view.vue_abstraite import VueAbstraite
from view.session import Session

# Supprimés car cette vue n'accède plus directement à la BDD
# (sauf pour les stats, mais on pourrait aussi le migrer)
# from dao.qrcode_dao import QRCodeDao
# from service.qrcode_service import QRCodeService
# from dao.db_connection import DBConnection

# URL de base de l'API. S'attend à ce que l'API FastAPI tourne localement sur le port 5000
# Surchargez-la dans votre .env si l'API est ailleurs
# MODIFIÉ : Utilise BASE_API_URL pour correspondre à votre .env
API_BASE_URL = os.getenv("BASE_API_URL", "http://127.0.0.1:5000")


class MenuUtilisateurVue(VueAbstraite):
    """Menu utilisateur: session, mes QR codes, stats de mes QR, création, déconnexion"""

    def _get_current_user(self):
        # ... (code existant inchangé) ...
        sess = Session()
        return getattr(sess, "user", None) or getattr(sess, "joueur", None) or getattr(sess, "utilisateur", None)

    def _build_scan_url(self, qr_id: int) -> str:
        # ... (code existant inchangé) ...
        scan_base = os.getenv("SCAN_BASE_URL")
        tracking_base = os.getenv("TRACKING_BASE_URL", "https://monapi.example.com/r")
        base = (scan_base or tracking_base).rstrip("/")
        return f"{base}/{qr_id}"

    def choisir_menu(self):
        print("\n" + "-" * 50 + "\nMenu Utilisateur\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Infos de session",
                "Lister mes QR codes (via API)",
                "Voir statistiques d'un de MES QR (via API)", # Modifié
                "Créer un QR code (via API)",
                "Se déconnecter",
            ],
        ).execute()

        match choix:
            case "Se déconnecter":
                # ... (code existant inchangé) ...
                Session().deconnexion()
                from view.accueil.accueil_vue import AccueilVue
                return AccueilVue()

            case "Infos de session":
                # ... (code existant inchangé) ...
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

                    # 2. Construire l'URL de l'API
                    api_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/utilisateur/{str(id_user)}"
                    print(f"Appel de l'API GET {api_endpoint}...")

                    # 3. Appeler l'API
                    response = requests.get(api_endpoint, timeout=10)
                    response.raise_for_status()  # Lève une erreur si statut 4xx ou 5xx

                    # 4. Traiter la réponse JSON (une liste de dictionnaires)
                    qrs_data = response.json()
                    if not qrs_data:
                        return MenuUtilisateurVue(f"Aucun QR code trouvé pour {nom_user} via l'API.")

                    # 5. Formater la sortie comme demandé
                    lignes = [f"QR codes de {nom_user}:"]
                    for q in qrs_data:  # q est un dictionnaire
                        iq = q.get("id_qrcode", "?")
                        url = q.get("url", "N/A")
                        date_creation_iso = q.get("date_creation", None)
                        
                        # Formater la date pour n'afficher que YYYY-MM-DD
                        date_str = "N/A"
                        if date_creation_iso:
                            try:
                                date_str = date_creation_iso.split('T')[0]
                            except Exception:
                                date_str = date_creation_iso  # Fallback

                        lignes.append(f"- #{iq} (créé le {date_str}) → {url}")
                    
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
                    if not mes_qr_data:
                        return MenuUtilisateurVue("Aucun QR code pour cet utilisateur.")

                    # Construit les options pour InquirerPy
                    options = [f"#{q.get('id_qrcode', '?')} {q.get('url', '')}" for q in mes_qr_data]
                    selection = inquirer.select(
                        message="Choisissez un QR (seuls les vôtres sont listés) :",
                        choices=options,
                    ).execute()

                    try:
                        id_qr = int(selection.split()[0].lstrip("#"))
                    except Exception:
                        return MenuUtilisateurVue("Sélection invalide.")

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
                    
                    # Helper pour formater les dates (YYYY-MM-DD)
                    def format_date(iso_string):
                        if not iso_string: return 'N/A'
                        try: return iso_string.split('T')[0]
                        except Exception: return iso_string

                    lignes.append(f"Total vues: {stats_data.get('total_vues', 0)}")
                    lignes.append(f"Première vue: {format_date(stats_data.get('premiere_vue'))}")
                    lignes.append(f"Dernière vue: {format_date(stats_data.get('derniere_vue'))}")
                    
                    par_jour = stats_data.get("par_jour", [])
                    if par_jour:
                        lignes.append("Détail par jour:")
                        for r in par_jour: # r est un dict {"date": "...", "vues": ...}
                            d = format_date(r.get("date"))
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
                    return MenuUtilisateurVue(f"Erreur API: {http_err.response.status_code} - {detail}")
                except requests.exceptions.RequestException as req_err:
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur lors de la récupération des statistiques: {e}")


            case "Créer un QR code (via API)":
                # ... (code existant inchangé) ...
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
                        f"- url encodée (scan API): {response_data.get('scan_url')}",
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

