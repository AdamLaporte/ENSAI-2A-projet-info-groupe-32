from InquirerPy import inquirer
import os
import requests
import json
from datetime import datetime, timedelta

from view.vue_abstraite import VueAbstraite
from view.session import Session

# URL de base de l'API. Doit correspondre à votre .env
API_BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


class MenuUtilisateurVue(VueAbstraite):
    """Menu utilisateur: session, mes QR codes, stats de mes QR, création, déconnexion"""

    def _get_current_user(self):
        sess = Session()
        return (
            getattr(sess, "user", None)
            or getattr(sess, "joueur", None)
            or getattr(sess, "utilisateur", None)
        )

    def _get_auth_headers(self):
        """Récupère le token de la session et le formate pour les requêtes API."""
        token = getattr(Session(), "access_token", None)
        if not token:
            raise ValueError(
                "Token API non trouvé dans la session. Veuillez vous reconnecter."
            )
        return {"Authorization": f"Bearer {token}"}

    def _build_scan_url(self, qr_id: int) -> str:
        scan_base = os.getenv("SCAN_BASE_URL")
        if not scan_base:
            print("AVERTISSEMENT: SCAN_BASE_URL n'est pas défini dans .env")
            return f"URL_SCAN_NON_DEFINIE/{qr_id}"

        base = scan_base.rstrip("/")
        return f"{base}/{qr_id}"

    def _format_date(self, iso_string):
        if not iso_string:
            return "N/A"
        try:
            return iso_string.split("T")[0]
        except Exception:
            return iso_string

    # --- HELPER POUR FORMATER DATE ET HEURE ---
    def _format_datetime(self, iso_string):
        if not iso_string:
            return "N/A"
        try:
            if iso_string.endswith("Z"):
                iso_string = iso_string[:-1] + "+00:00"

            dt = datetime.fromisoformat(iso_string)

            dt_modifiee = dt + timedelta(hours=1)

            return dt_modifiee.strftime("Le %d/%m/%Y à %H:%M:%S")
        except Exception:
            return iso_string

    # --- HELPER POUR TRONQUER LE TEXTE ---
    def _truncate(self, text, max_len=40):
        if not text:
            return "N/A"
        text = str(text)
        return (text[:max_len] + "...") if len(text) > max_len else text

    # --- HELPERS DE PARSING ---
    def _parse_language(self, lang_string):
        """Extrait la langue principale (ex: FR) de 'fr-FR,fr;q=0.9'."""
        if not lang_string:
            return "N/A"
        try:
            first_lang = lang_string.split(",")[0]
            main_lang = first_lang.split("-")[0]
            return main_lang.upper()
        except Exception:
            return self._truncate(lang_string, 5)

    def _parse_device(self, agent_string):
        """Tente de deviner l'appareil depuis le User-Agent."""
        if not agent_string:
            return "Inconnu"
        agent_lower = agent_string.lower()
        if "android" in agent_lower:
            return "Android"
        if "iphone" in agent_lower:
            return "iPhone"
        if "ipad" in agent_lower:
            return "iPad"
        if "windows" in agent_lower:
            return "Windows"
        if "macintosh" in agent_lower or "mac os x" in agent_lower:
            return "Mac"
        if "linux" in agent_lower:
            return "Linux"
        return "Autre"

    # --- NOUVEL HELPER GÉO ---
    def _format_geo(self, city, country, client_ip):
        """Formate la sortie Géo."""
        if city and country:
            return f"📍 {city}, {country}"
        if country:
            return f"📍 {country}"
        if client_ip:
            return f"🌍 {client_ip}"
        return "Localisation inconnue"

    def choisir_menu(self):
        print("\n" + "-" * 50 + "\nMenu Utilisateur\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Infos de session",
                "Lister mes QR codes (via API)",
                "Voir statistiques d'un de MES QR (via API)",
                "Créer un QR code (via API)",
                "Modifier un QR code (via API)",
                "Supprimer un QR code (via API)",
                "Se déconnecter",
            ],
        ).execute()

        match choix:
            case "Se déconnecter":
                Session().deconnexion()
                from view.accueil.accueil_vue import AccueilVue

                return AccueilVue("Vous avez été déconnecté.")

            case "Modifier un QR code (via API)":
                try:
                    auth_headers = self._get_auth_headers()

                    list_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/utilisateur/me"
                    print(f"Appel de l'API GET {list_endpoint} pour lister vos QRs...")
                    list_response = requests.get(
                        list_endpoint, headers=auth_headers, timeout=10
                    )
                    list_response.raise_for_status()
                    mes_qr_data = list_response.json()

                    if not mes_qr_data:
                        return MenuUtilisateurVue(
                            "Vous n'avez aucun QR code à modifier."
                        )

                    options = [
                        f"#{q.get('id_qrcode', '?')} → {self._truncate(q.get('url', 'N/A'), 50)}"
                        for q in mes_qr_data
                    ]
                    options.append("--- ANNULER ---")

                    selection = inquirer.select(
                        message="Choisissez un QR code à MODIFIER :",
                        choices=options,
                    ).execute()

                    if selection == "--- ANNULER ---":
                        return MenuUtilisateurVue("Modification annulée.")

                    id_qr = int(selection.split()[0].lstrip("#"))

                    selected_qr = next(
                        (q for q in mes_qr_data if q.get("id_qrcode") == id_qr), {}
                    )

                    print(f"\nURL actuelle : {selected_qr.get('url', 'N/A')}")
                    nouvelle_url = (
                        inquirer.text(
                            message="Entrez la nouvelle URL de destination (ou laissez vide pour ne pas changer) :",
                            default="",
                        )
                        .execute()
                        .strip()
                    )

                    if not nouvelle_url:
                        return MenuUtilisateurVue(
                            "Aucune modification fournie. Opération annulée."
                        )

                    update_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/{id_qr}"
                    payload = {"url": nouvelle_url}

                    print(f"Appel de l'API PUT {update_endpoint}...")

                    response = requests.put(
                        update_endpoint, json=payload, headers=auth_headers, timeout=10
                    )

                    response.raise_for_status()

                    return MenuUtilisateurVue(f"Le QR code #{id_qr} a été mis à jour.")

                except (requests.exceptions.HTTPError, ValueError) as err:
                    detail = str(err)
                    if isinstance(err, requests.exceptions.HTTPError):
                        try:
                            detail = err.response.json().get(
                                "detail", err.response.text
                            )
                        except json.JSONDecodeError:
                            detail = err.response.text
                    return MenuUtilisateurVue(f"Erreur: {detail}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur lors de la modification: {e}")

            case "Supprimer un QR code (via API)":
                try:
                    auth_headers = self._get_auth_headers()

                    list_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/utilisateur/me"
                    print(f"Appel de l'API GET {list_endpoint} pour lister vos QRs...")
                    list_response = requests.get(
                        list_endpoint, headers=auth_headers, timeout=10
                    )
                    list_response.raise_for_status()

                    mes_qr_data = list_response.json()

                    if not mes_qr_data:
                        return MenuUtilisateurVue(
                            "Vous n'avez aucun QR code à supprimer."
                        )

                    options = []
                    for q in mes_qr_data:
                        suivi_str = (
                            "(Suivi)" if q.get("type_qrcode") is True else "(Non-suivi)"
                        )
                        url_tronquee = self._truncate(q.get("url", "N/A"), max_len=50)
                        options.append(
                            f"#{q.get('id_qrcode', '?')} {suivi_str} → {url_tronquee}"
                        )

                    options.append("--- ANNULER ---")

                    selection = inquirer.select(
                        message="Choisissez un QR code à SUPPRIMER :",
                        choices=options,
                    ).execute()

                    if selection == "--- ANNULER ---":
                        return MenuUtilisateurVue("Suppression annulée.")

                    try:
                        id_qr = int(selection.split()[0].lstrip("#"))
                    except Exception:
                        return MenuUtilisateurVue("Sélection invalide.")

                    confirmation = inquirer.confirm(
                        message=f"Êtes-vous certain de vouloir supprimer le QR code #{id_qr} ?\nCette action est irréversible.",
                        default=False,
                    ).execute()

                    if not confirmation:
                        return MenuUtilisateurVue("Suppression annulée.")

                    delete_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/{id_qr}"
                    print(f"Appel de l'API DELETE {delete_endpoint}...")

                    response = requests.delete(
                        delete_endpoint, headers=auth_headers, timeout=10
                    )

                    response.raise_for_status()

                    return MenuUtilisateurVue(
                        f"Le QR code #{id_qr} a été supprimé avec succès."
                    )

                except (requests.exceptions.HTTPError, ValueError) as err:
                    detail = str(err)
                    if isinstance(err, requests.exceptions.HTTPError):
                        try:
                            detail = err.response.json().get(
                                "detail", err.response.text
                            )
                        except json.JSONDecodeError:
                            detail = err.response.text
                    return MenuUtilisateurVue(f"Erreur: {detail}")
                except requests.exceptions.RequestException as req_err:
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur lors de la suppression: {e}")

            case "Infos de session":
                return MenuUtilisateurVue(Session().afficher())

            case "Lister mes QR codes (via API)":
                try:
                    auth_headers = self._get_auth_headers()
                    user = self._get_current_user()
                    nom_user = getattr(user, "nom_user", "Utilisateur")

                    if not user:
                        return MenuUtilisateurVue(
                            "Impossible de déterminer l'id utilisateur."
                        )

                    api_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/utilisateur/me"
                    print(f"Appel de l'API GET {api_endpoint}...")

                    response = requests.get(
                        api_endpoint, headers=auth_headers, timeout=10
                    )
                    response.raise_for_status()

                    qrs_data = response.json()
                    if not qrs_data:
                        return MenuUtilisateurVue(
                            f"Aucun QR code trouvé pour {nom_user} via l'API."
                        )

                    print("\nFiltrer la liste de vos QR codes :")
                    filter_choice = inquirer.select(
                        message="Afficher :",
                        choices=[
                            "Tous",
                            "Uniquement les QR suivis",
                            "Uniquement les QR non-suivis",
                        ],
                        default="Tous",
                    ).execute()

                    filtered_list = []
                    if filter_choice == "Tous":
                        filtered_list = qrs_data
                    elif filter_choice == "Uniquement les QR suivis":
                        filtered_list = [
                            q for q in qrs_data if q.get("type_qrcode") is True
                        ]
                    else:
                        filtered_list = [
                            q for q in qrs_data if q.get("type_qrcode") is False
                        ]

                    if not filtered_list:
                        return MenuUtilisateurVue(
                            "Aucun QR code ne correspond à ce filtre."
                        )

                    print("\nSélectionnez un QR code pour voir les détails :")
                    options = []
                    for q in filtered_list:
                        suivi_str = (
                            "(Suivi)" if q.get("type_qrcode") is True else "(Non-suivi)"
                        )
                        options.append(
                            f"#{q.get('id_qrcode', '?')} {suivi_str} → {q.get('url', 'N/A')}"
                        )

                    selection = inquirer.select(
                        message="Vos QR codes filtrés :",
                        choices=options,
                    ).execute()

                    try:
                        id_qr_str = selection.split(" ")[0].lstrip("#")
                        id_qr = int(id_qr_str)
                    except Exception:
                        return MenuUtilisateurVue("Sélection invalide.")

                    selected_qr = next(
                        (q for q in filtered_list if q.get("id_qrcode") == id_qr), None
                    )

                    if not selected_qr:
                        return MenuUtilisateurVue(
                            f"Erreur: impossible de retrouver les détails du QR #{id_qr}."
                        )

                    titre = f"Détails du QR code #{id_qr}"
                    lignes = ["\n" + titre, "-" * len(titre)]
                    lignes.append(
                        f"URL de destination: {selected_qr.get('url', 'N/A')}"
                    )
                    lignes.append(
                        f"Date de création:   {self._format_date(selected_qr.get('date_creation'))}"
                    )

                    if selected_qr.get("type_qrcode") is True:
                        lignes.append(f"Type:               Suivi (Dynamique)")
                        lignes.append(
                            f"URL de scan (encodée): {selected_qr.get('scan_url', 'N/A')}"
                        )
                        lignes.append(
                            f"URL de l'image:     {selected_qr.get('image_url', 'N/A')}"
                        )
                        lignes.append(
                            "Statistiques:       Disponibles (via le menu 'Voir statistiques')"
                        )
                    else:
                        lignes.append(f"Type:               Non-suivi (Classique)")
                        lignes.append(
                            f"URL de scan (encodée): N/A (l'URL de destination est encodée directement)"
                        )
                        lignes.append(
                            f"URL de l'image:     {selected_qr.get('image_url', 'N/A')}"
                        )
                        lignes.append("Statistiques:       Non disponibles")

                    lignes.append(
                        f"Couleur:            {selected_qr.get('couleur', 'N/A')}"
                    )
                    lignes.append(
                        f"Logo:               {selected_qr.get('logo') or 'aucun'}"
                    )

                    return MenuUtilisateurVue("\n".join(lignes))

                except (requests.exceptions.HTTPError, ValueError) as err:
                    detail = str(err)
                    if isinstance(err, requests.exceptions.HTTPError):
                        try:
                            detail = err.response.json().get(
                                "detail", err.response.text
                            )
                        except json.JSONDecodeError:
                            detail = err.response.text
                    return MenuUtilisateurVue(f"Erreur: {detail}")
                except requests.exceptions.RequestException as req_err:
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur inattendue : {e}")

            case "Voir statistiques d'un de MES QR (via API)":
                try:
                    auth_headers = self._get_auth_headers()
                    user = self._get_current_user()
                    if not user:
                        return MenuUtilisateurVue(
                            "Impossible de déterminer l'id utilisateur."
                        )

                    list_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/utilisateur/me"
                    print(f"Appel de l'API GET {list_endpoint} pour lister vos QRs...")
                    list_response = requests.get(
                        list_endpoint, headers=auth_headers, timeout=10
                    )
                    list_response.raise_for_status()

                    mes_qr_data = list_response.json()
                    qr_suivis = [q for q in mes_qr_data if q.get("type_qrcode") is True]

                    if not qr_suivis:
                        return MenuUtilisateurVue(
                            "Vous n'avez aucun QR code 'suivi' pour lequel voir des stats."
                        )

                    options = [
                        f"#{q.get('id_qrcode', '?')} {q.get('url', '')}"
                        for q in qr_suivis
                    ]
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
                    stats_response = requests.get(
                        stats_endpoint, headers=auth_headers, timeout=10
                    )
                    stats_response.raise_for_status()

                    stats_data = stats_response.json()

                    scan_url = self._build_scan_url(id_qr)

                    titre = f"Statistiques de votre QR #{id_qr}"
                    lignes = [titre, "-" * len(titre)]
                    lignes.append(f"URL de scan API: {scan_url}")

                    lignes.append(f"Total vues: {stats_data.get('total_vues', 0)}")
                    lignes.append(
                        f"Première vue: {self._format_date(stats_data.get('premiere_vue'))}"
                    )
                    lignes.append(
                        f"Dernière vue: {self._format_date(stats_data.get('derniere_vue'))}"
                    )

                    par_jour = stats_data.get("par_jour", [])
                    if par_jour:
                        lignes.append("Détail par jour (agrégé):")
                        for r in par_jour:
                            d = self._format_date(r.get("date"))
                            v = r.get("vues", 0)
                            lignes.append(f"- {d}: {v}")
                    else:
                        lignes.append(
                            "Détail par jour (agrégé): Aucune vue enregistrée."
                        )

                    scans_recents = stats_data.get("scans_recents", [])
                    if scans_recents:
                        lignes.append("\nScans récents (détaillés):")
                        for log in scans_recents:
                            timestamp_str = self._format_datetime(log.get("timestamp"))
                            client_ip = log.get("client", "IP inconnue")
                            lang = self._parse_language(log.get("language"))
                            device = self._parse_device(log.get("user_agent"))

                            city = log.get("geo_city")
                            country = log.get("geo_country")
                            geo_str = self._format_geo(city, country, client_ip)

                            lignes.append(
                                f"  • {timestamp_str} | 📱 {device:<8} | 🌐 {lang:<3} | {geo_str} ({client_ip})"
                            )
                    else:
                        lignes.append(
                            "\nScans récents (détaillés): Aucun scan individuel trouvé."
                        )

                    return MenuUtilisateurVue("\n".join(lignes))

                except (requests.exceptions.HTTPError, ValueError) as err:
                    detail = str(err)
                    if isinstance(err, requests.exceptions.HTTPError):
                        try:
                            detail = err.response.json().get(
                                "detail", err.response.text
                            )
                        except json.JSONDecodeError:
                            detail = err.response.text
                    return MenuUtilisateurVue(f"Erreur: {detail}")
                except requests.exceptions.RequestException as req_err:
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(
                        f"Erreur lors de la récupération des statistiques: {e}"
                    )

            case "Créer un QR code (via API)":
                try:
                    auth_headers = self._get_auth_headers()
                    user = self._get_current_user()
                    id_user = getattr(user, "id_user", None)
                    if not id_user:
                        return MenuUtilisateurVue(
                            "Impossible de déterminer l'id utilisateur."
                        )

                    url = inquirer.text(message="URL cible du QR : ").execute().strip()
                    if not url:
                        return MenuUtilisateurVue("URL vide, opération annulée.")

                    is_tracked = inquirer.confirm(
                        message="Activer le suivi (statistiques) pour ce QR code ?",
                        default=True,
                    ).execute()

                    couleurs = [
                        "black",
                        "blue",
                        "red",
                        "green",
                        "purple",
                        "teal",
                        "orange",
                        "gray",
                    ]
                    couleur = inquirer.select(
                        message="Couleur du QR : ",
                        choices=couleurs,
                        default="black",
                    ).execute()

                    logo = (
                        inquirer.text(
                            message="Chemin du logo (optionnel, Enter pour passer) : "
                        )
                        .execute()
                        .strip()
                    )
                    logo = logo if logo else None

                    api_endpoint = f"{API_BASE_URL.rstrip('/')}/qrcode/"
                    payload = {
                        "url": url,
                        "id_proprietaire": str(id_user),
                        "type_qrcode": is_tracked,
                        "couleur": couleur,
                        "logo": logo,
                    }

                    print(f"Appel de l'API POST {api_endpoint}...")

                    response = requests.post(
                        api_endpoint, json=payload, headers=auth_headers, timeout=10
                    )
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
                        f"\nL'image a été sauvegardée sur le serveur (dans {os.getenv('QRCODE_OUTPUT_DIR', 'static/qrcodes')})",
                    ]
                    return MenuUtilisateurVue("\n".join(lignes))

                except (requests.exceptions.HTTPError, ValueError) as err:
                    detail = str(err)
                    if isinstance(err, requests.exceptions.HTTPError):
                        try:
                            detail = err.response.json().get(
                                "detail", err.response.text
                            )
                        except json.JSONDecodeError:
                            detail = err.response.text
                    return MenuUtilisateurVue(f"Erreur: {detail}")
                except requests.exceptions.RequestException as req_err:
                    return MenuUtilisateurVue(f"Erreur de connexion à l'API: {req_err}")
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur inattendue : {e}")

        return self
