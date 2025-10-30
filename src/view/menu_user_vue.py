# src/view/menu_user_vue.py
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session

from dao.qrcode_dao import QRCodeDao
from service.qrcode_service import QRCodeService
from dao.db_connection import DBConnection


class MenuUtilisateurVue(VueAbstraite):
    """Menu utilisateur: session, mes QR codes, stats de mes QR, déconnexion"""

    def _get_current_user(self):
        # Centralise la récupération de l'utilisateur depuis la Session
        sess = Session()
        return getattr(sess, "user", None) or getattr(sess, "joueur", None) or getattr(sess, "utilisateur", None)

    def choisir_menu(self):
        print("\n" + "-" * 50 + "\nMenu Utilisateur\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Infos de session",
                "Lister mes QR codes",
                "Voir statistiques d'un de MES QR",
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

            case "Lister mes QR codes":
                try:
                    user = self._get_current_user()
                    if user is None:
                        return MenuUtilisateurVue("Non connecté.")
                    id_user = getattr(user, "id_user", None)
                    if not id_user:
                        return MenuUtilisateurVue("Impossible de déterminer l'id utilisateur.")

                    qsvc = QRCodeService(QRCodeDao())
                    qrs = qsvc.trouver_qrc_par_id_user(str(id_user))
                    if not qrs:
                        return MenuUtilisateurVue("Aucun QR code pour cet utilisateur.")

                    lignes = [f"QR codes de {getattr(user, 'nom_user', id_user)}:"]
                    for q in qrs:
                        url = getattr(q, "url", "")
                        iq = getattr(q, "id_qrcode", "?")
                        lignes.append(f"- #{iq} → {url}")
                    return MenuUtilisateurVue("\n".join(lignes))
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur lors du listing de vos QR: {e}")

            case "Voir statistiques d'un de MES QR":
                try:
                    # 1) Utilisateur connecté
                    user = self._get_current_user()
                    if user is None:
                        return MenuUtilisateurVue("Non connecté.")
                    id_user = getattr(user, "id_user", None)
                    if not id_user:
                        return MenuUtilisateurVue("Impossible de déterminer l'id utilisateur.")

                    # 2) Lister uniquement MES QR et proposer un choix
                    qsvc = QRCodeService(QRCodeDao())
                    mes_qr = qsvc.trouver_qrc_par_id_user(str(id_user))
                    if not mes_qr:
                        return MenuUtilisateurVue("Aucun QR code pour cet utilisateur.")

                    options = [f"#{getattr(q, 'id_qrcode', '?')} {getattr(q, 'url', '')}" for q in mes_qr]
                    selection = inquirer.select(
                        message="Choisissez un QR (seuls les vôtres sont listés) :",
                        choices=options,
                    ).execute()

                    try:
                        id_qr = int(selection.split()[0].lstrip("#"))
                    except Exception:
                        return MenuUtilisateurVue("Sélection invalide.")

                    # 3) Stats pour CET id (synthèse + détail)
                    with DBConnection().connection as conn:
                        with conn.cursor() as cur:
                            cur.execute(
                                """
                                SELECT
                                    COALESCE(SUM(nombre_vue), 0) AS total_vues,
                                    MIN(date_des_vues) AS premiere_vue,
                                    MAX(date_des_vues) AS derniere_vue
                                FROM statistique
                                WHERE id_qrcode = %s
                                """,
                                (id_qr,),
                            )
                            agg = cur.fetchone() or {}
                            total = agg.get("total_vues", 0)
                            premiere = agg.get("premiere_vue")
                            derniere = agg.get("derniere_vue")

                            cur.execute(
                                """
                                SELECT date_des_vues, nombre_vue
                                FROM statistique
                                WHERE id_qrcode = %s
                                ORDER BY date_des_vues ASC
                                """,
                                (id_qr,),
                            )
                            rows = cur.fetchall() or []

                    titre = f"Statistiques de votre QR #{id_qr}"
                    lignes = [titre, "-" * len(titre)]
                    lignes.append(f"Total vues: {int(total) if total is not None else 0}")
                    lignes.append(f"Première vue: {premiere if premiere else 'N/A'}")
                    lignes.append(f"Dernière vue: {derniere if derniere else 'N/A'}")
                    if rows:
                        lignes.append("Détail par jour:")
                        for r in rows:
                            d = r["date_des_vues"]
                            v = r["nombre_vue"]
                            lignes.append(f"- {d}: {v}")

                    return MenuUtilisateurVue("\n".join(lignes))
                except Exception as e:
                    return MenuUtilisateurVue(f"Erreur lors de la récupération des statistiques: {e}")

        # Par défaut on reste sur le menu
        return self
