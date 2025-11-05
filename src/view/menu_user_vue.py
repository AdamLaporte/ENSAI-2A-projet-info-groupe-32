from InquirerPy import inquirer
import os
import requests  # Ajout pour les requêtes HTTP
import json      # Ajout pour formater le payload
from datetime import datetime # Ajout pour parser les timestamps

from view.vue_abstraite import VueAbstraite
from view.session import Session

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

    # --- HELPER POUR FORMATER DATE ET HEURE ---
    def _format_datetime(self, iso_string):
        if not iso_string: return 'N/A'
        try:
            # Gère le 'Z' (UTC) si présent
            if iso_string.endswith('Z'):
                iso_string = iso_string[:-1] + '+00:00'
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("Le %d/%m/%Y à %H:%M:%S")
        except Exception:
            return iso_string

    # --- HELPER POUR TRONQUER LE TEXTE ---
    def _truncate(self, text, max_len=40):
        if not text: return "N/A"
        text = str(text)
        return (text[:max_len] + '...') if len(text) > max_len else text

    # --- HELPERS DE PARSING ---
    def _parse_language(self, lang_string):
        """Extrait la langue principale (ex: FR) de 'fr-FR,fr;q=0.9'."""
        if not lang_string: return "N/A"
        try:
            first_lang = lang_string.split(',')[0]
            main_lang = first_lang.split('-')[0]
            return main_lang.upper()
        except Exception:
            return self._truncate(lang_string, 5) 

    def _parse_device(self, agent_string):
        """Tente de deviner l'appareil depuis le User-Agent."""
        if not agent_string: return "Inconnu"
        agent_lower = agent_string.lower()
        if "android" in agent_lower: return "Android"
        if "iphone" in agent_lower: return "iPhone"
        if "ipad" in agent_lower: return "iPad"
        if "windows" in agent_lower: return "Windows"
        if "macintosh" in agent_lower or "mac os x" in agent_lower: return "Mac"
        if "linux" in agent_lower: return "Linux"
        return "Autre"
        
    # --- NOUVEL HELPER GÉO ---
    def _format_geo(self, city, country, client_ip):
        """Formate la sortie Géo."""
        if city and country:
            return f"📍 {city}, {country}"
        if country:
            return f"📍 {country}"
        if client_ip:
            # Fallback to IP if no geo data (ex: IP locale)
            return f"🌍 {client_ip}"
        return "Localisation inconnue"
    # --- FIN DE L'AJOUT ---


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
                    user = self._get_current_user()
                    if user is None:
                        return MenuUtilisateurVue("Non connecté.")
                    
                    id_user = getattr(user, "id_user", None)
                    nom_user = getattr(user, 'nom_user', id_user)
                    
                    if not id_user:
                        return MenuUtilisateurVue("Impossible de déterminer l'id utilisateur.")

                    api_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/utilisateur/{str(id_user)}"
                    print(f"Appel de l'API GET {api_endpoint}...")

                    response = requests.get(api_endpoint, timeout=10)
                    response.raise_for_status() 

                    qrs_data = response.json()
                    if not qrs_data:
                        return MenuUtilisateurVue(f"Aucun QR code trouvé pour {nom_user} via l'API.")

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
                        filtered_list = [q for q in qrs_data if q.get("type") is True]
                    else: 
                        filtered_list = [q for q in qrs_data if q.get("type") is False]

                    if not filtered_list:
                        return MenuUtilisateurVue("Aucun QR code ne correspond à ce filtre.")

                    print("\nSélectionnez un QR code pour voir les détails :")
                    options = []
                    for q in filtered_list:
                        suivi_str = "(Suivi)" if q.get("type") is True else "(Non-suivi)"
                        options.append(f"#{q.get('id_qrcode', '?')} {suivi_str} → {q.get('url', 'N/A')}")
                    
                    selection = inquirer.select(
                        message="Vos QR codes filtrés :",
                        choices=options,
                    ).execute()
                    
                    try:
                        id_qr_str = selection.split(' ')[0].lstrip("#")
                        id_qr = int(id_qr_str)
                    except Exception:
                        return MenuUtilisateurVue("Sélection invalide.")

                    selected_qr = next((q for q in filtered_list if q.get("id_qrcode") == id_qr), None)
                    
                    if not selected_qr:
                         return MenuUtilisateurVue(f"Erreur: impossible de retrouver les détails du QR #{id_qr}.")

                    titre = f"Détails du QR code #{id_qr}"
                    lignes = ["\n" + titre, "-" * len(titre)]
                    lignes.append(f"URL de destination: {selected_qr.get('url', 'N/A')}")
                    lignes.append(f"Date de création:   {self._format_date(selected_qr.get('date_creation'))}")
                    
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
                    try:
                        detail = http_err.response.json().get('detail', http_err)
                    except json.JSONDecodeError:
                        detail = http_err.response.text
                    return MenuUtilisateurVue(f"Erreur API: {http_err.response.status_code} - {detail}")
                except requests.exceptions.RequestException as req_err:
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur inattendue : {e}")


            case "Voir statistiques d'un de MES QR (via API)":
                try:
                    user = self._get_current_user()
                    if user is None:
                        return MenuUtilisateurVue("Non connecté.")
                    id_user = getattr(user, "id_user", None)
                    if not id_user:
                        return MenuUtilisateurVue("Impossible de déterminer l'id utilisateur.")

                    list_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/utilisateur/{str(id_user)}"
                    print(f"Appel de l'API GET {list_endpoint} pour lister vos QRs...")
                    list_response = requests.get(list_endpoint, timeout=10)
                    list_response.raise_for_status()
                    
                    mes_qr_data = list_response.json()
                    qr_suivis = [q for q in mes_qr_data if q.get("type") is True]
                    
                    if not qr_suivis:
                        return MenuUtilisateurVue("Vous n'avez aucun QR code 'suivi' pour lequel voir des stats.")

                    options = [f"#{q.get('id_qrcode', '?')} {q.get('url', '')}" for q in qr_suivis]
                    selection = inquirer.select(
                        message="Choisissez un QR code 'suivi' :",
                        choices=options,
                    ).execute()

                    try:
                        id_qr = int(selection.split()[0].lstrip("#"))
                    except Exception:
                        return MenuUtilisateurVue("Sélection invalide.")

                    stats_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/{id_qr}/stats"
                    print(f"Appel de l'API GET {stats_endpoint}...")
                    stats_response = requests.get(stats_endpoint, timeout=10)
                    stats_response.raise_for_status()
                    
                    stats_data = stats_response.json() 

                    scan_url = self._build_scan_url(id_qr)

                    titre = f"Statistiques de votre QR #{id_qr}"
                    lignes = [titre, "-" * len(titre)]
                    lignes.append(f"URL de scan API: {scan_url}")
                    
                    lignes.append(f"Total vues: {stats_data.get('total_vues', 0)}")
                    lignes.append(f"Première vue: {self._format_date(stats_data.get('premiere_vue'))}")
                    lignes.append(f"Dernière vue: {self._format_date(stats_data.get('derniere_vue'))}")
                    
                    par_jour = stats_data.get("par_jour", [])
                    if par_jour:
                        lignes.append("Détail par jour (agrégé):")
                        for r in par_jour: 
                            d = self._format_date(r.get("date"))
                            v = r.get("vues", 0)
                            lignes.append(f"- {d}: {v}")
                    else:
                        lignes.append("Détail par jour (agrégé): Aucune vue enregistrée.")

                    # --- BLOC MODIFIÉ : Affichage graphique avec GÉO ---
                    scans_recents = stats_data.get("scans_recents", [])
                    if scans_recents:
                        lignes.append("\nScans récents (détaillés):")
                        for log in scans_recents:
                            timestamp_str = self._format_datetime(log.get("timestamp"))
                            client_ip = log.get("client", "IP inconnue")
                            lang = self._parse_language(log.get("language"))
                            device = self._parse_device(log.get("user_agent"))
                            
                            # --- AJOUT GÉO ---
                            city = log.get("geo_city")
                            country = log.get("geo_country")
                            geo_str = self._format_geo(city, country, client_ip)
                            # --- FIN AJOUT GÉO ---
                            
                            # Formatage aligné
                            # ex: • Le 05/11/2025 à 11:17:38 | 📱 Windows   | 🌐 FR  | 📍 Rennes, France
                            lignes.append(f"  • {timestamp_str} | 📱 {device:<8} | 🌐 {lang:<3} | {geo_str} ({client_ip})")
                    else:
                        lignes.append("\nScans récents (détaillés): Aucun scan individuel trouvé.")
                    # --- FIN DU BLOC MODIFIÉ ---

                    return MenuUtilisateurVue("\n".join(lignes))
                
                except requests.exceptions.HTTPError as http_err:
                    try:
                        detail = http_err.response.json().get('detail', http_err)
                    except json.JSONDecodeError:
                        detail = http_err.response.text
                    if http_err.response.status_code == 404:
                         return MenuUtilisateurVue(f"Info: {detail}")
                    return MenuUtilisateurVue(f"Erreur API: {http_err.response.status_code} - {detail}")
                except requests.exceptions.RequestException as req_err:
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur lors de la récupération des statistiques: {e}")


            case "Créer un QR code (via API)":
                try:
                    user = self._get_current_user()
                    if user is None:
                        return MenuUtilisateurVue("Non connecté.")
                    id_user = getattr(user, "id_user", None)
                    if not id_user:
                        return MenuUtilisateurVue("Impossible de déterminer l'id utilisateur.")

                    url = inquirer.text(message="URL cible du QR : ").execute().strip()
                    if not url:
                        return MenuUtilisateurVue("URL vide, opération annulée.")

                    is_tracked = inquirer.confirm(
                        message="Activer le suivi (statistiques) pour ce QR code ?",
                        default=True,
                    ).execute()

                    couleurs = ["black", "blue", "red", "green", "purple", "teal", "orange", "gray"]
                    couleur = inquirer.select(
                        message="Couleur du QR : ",
                        choices=couleurs,
                        default="black",
                    ).execute()

                    logo = inquirer.text(message="Chemin du logo (optionnel, Enter pour passer) : ").execute().strip()
                    logo = logo if logo else None

                    api_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/"
                    payload = {
                        "url": url,
                        "id_proprietaire": str(id_user), 
                        "type_qrcode": is_tracked,
                        "couleur": couleur,
                        "logo": logo
                    }

                    print(f"Appel de l'API POST {api_endpoint}...")

                    response = requests.post(api_endpoint, json=payload, timeout=10)
                    response.raise_for_status() 
                    
                    response_data = response.json()
                    
                    lignes = [
                        "QR code créé avec succès via l'API:",
                        f"- id: {response_data.get('id_qrcode')}",
                        f"- url finale (redirection): {response_data.get('url')}",
                        f"- url encodée (scan API): {response_data.get('scan_url', 'N/A (suivi désactivé)')}",
                        f"- couleur: {response_data.get('couleur')}",
                        f"- logo: {response_data.get('logo') or 'aucun'}",
                        f"- image publique: {response_data.get('image_url')}",
                        f"\nL'image a été sauvegardée sur le serveur (dans {os.getenv('QRCODE_OUTPUT_DIR', 'static/qrcodes')})"
                    ]
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
                    return MenuUtilisateurVue(f"Erreur inattendue : {e}")

        # Par défaut on reste sur le menu
        return self