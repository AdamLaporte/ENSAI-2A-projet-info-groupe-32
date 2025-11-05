import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
# Ajout de FileResponse pour renvoyer des fichiers
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv


# ------------------------------------
# si app bloqué par un port :
# pkill -f "uvicorn" ou pkill -f "python.*app.py" depuis le terminal de l’environnement.
# ------------------------------------

load_dotenv()  # charge le .env dans os.environ

from service.qrcode_service import QRCodeService
from dao.qrcode_dao import QRCodeDao
from dao.db_connection import DBConnection

# Logging de base
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Initialisation de l'application ---
root_path = os.getenv("ROOT_PATH", "")
app = FastAPI(root_path=root_path)

# --- Définir le répertoire de sortie des images (utilisé par la route /image) ---
QR_OUTPUT_DIR = os.getenv("QRCODE_OUTPUT_DIR", "static/qrcodes")


# --- Initialisation du service ---
qrcode_service = QRCodeService(QRCodeDao())

# --- Modèles d’entrée pour l’API ---
class QRCodeCreateModel(BaseModel):
    url: str
    id_proprietaire: str
    type_qrcode: Optional[bool] = True
    couleur: Optional[str] = "noir"
    logo: Optional[str] = None

# -------------------------------------------------------------
# 🔹 ROUTES QR CODE CRUD
# -------------------------------------------------------------
@app.post("/qrcode/", tags=["QR Codes"])
async def creer_qrc(data: QRCodeCreateModel):
    """
    Créer un QR code, l'enregistrer et renvoyer ses détails 
    incluant l'URL de l'image et l'URL de scan.
    """
    try:
        # 1. Le service crée le QR en base ET génère l'image
        #    Il attache _scan_url et _image_url à l'objet 'created'
        created = qrcode_service.creer_qrc(
            url=data.url,
            id_proprietaire=data.id_proprietaire,
            type_=data.type_qrcode, # <-- MODIFIÉ: On passe le type
            couleur=data.couleur,
            logo=data.logo,
        )  # renvoie l'objet avec id

        # 2. Construire la réponse JSON manuellement
        #    On commence avec les données de base de l'objet
        response_data = created.to_dict()

        # 3. Ajouter les URLs générées par le service
        #    getattr() est utilisé pour éviter une erreur si l'attribut n'existe pas
        response_data["scan_url"] = getattr(created, '_scan_url', None)
        response_data["image_url"] = getattr(created, '_image_url', None)

        # 4. Renvoyer le JSON complet
        return JSONResponse(content=response_data, status_code=201)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur création QR code : %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/qrcode/utilisateur/{id_user}", tags=["QR Codes"])
async def qrcodes_par_utilisateur(id_user: str):
    """Lister tous les QR codes d’un utilisateur"""
    try:
        qrs = qrcode_service.trouver_qrc_par_id_user(id_user)
        # S'assurer que to_dict() est appelé sur chaque objet Qrcode
        return [q.to_dict() for q in qrs]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur récupération QR codes : %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/qrcode/{id_qrcode}", tags=["QR Codes"])
async def supprimer_qrcode(id_qrcode: int, id_user: str):
    """Supprimer un QR code (seulement par le propriétaire)"""
    try:
        ok = qrcode_service.supprimer_qrc(id_qrcode, id_user)
        if not ok:
            raise HTTPException(status_code=404, detail="QR code introuvable ou non autorisé")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur suppression QR code : %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# 🔹 ROUTE SCAN (tracking + redirection)
# -------------------------------------------------------------
@app.get("/scan/{id_qrcode}", include_in_schema=True, tags=["Scan"])
async def scan_qrcode(id_qrcode: int, request: Request):
    """
    Lorsqu'un utilisateur scanne le QR code :
    - on enregistre une statistique (date, +1) si le QR est 'suivi'
    - puis on redirige vers l'URL réelle
    """
    try:
        # Récupérer le QR cible
        qr = qrcode_service.dao.trouver_par_id(id_qrcode)
        if not qr:
            raise HTTPException(status_code=404, detail="QR code introuvable")

        # --- MODIFIÉ : Vérifier si le QR code est suivi ---
        # Si le type est False (non-suivi), on redirige sans compter
        if qr.type is False:
            logger.info(f"Scan NON enregistré (QR non-suivi) pour QRCode {id_qrcode}")
            return RedirectResponse(url=qr.url, status_code=307)
        # --- FIN DE LA MODIFICATION ---

        # Informations client (optionnel pour logs)
        user_agent = request.headers.get("user-agent", "inconnu")
        client_host = request.client.host if request.client else "inconnu"
        date_vue = datetime.utcnow() # Date ET heure

        # Enregistrement dans la table statistique (UPsert journalier)
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                # 1. Mise à jour de la table agrégée (par jour)
                cur.execute(
                    """
                    INSERT INTO statistique (id_qrcode, nombre_vue, date_des_vues)
                    VALUES (%s, 1, %s)
                    ON CONFLICT (id_qrcode, date_des_vues)
                    DO UPDATE SET nombre_vue = statistique.nombre_vue + 1;
                    """,
                    (id_qrcode, date_vue.date()), # On utilise .date() ici
                )

                # --- MODIFIÉ : Insérer dans le journal détaillé (avec l'heure) ---
                cur.execute(
                    """
                    INSERT INTO logs_scan (id_qrcode, client_host, user_agent, date_scan)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (id_qrcode, client_host, user_agent, date_vue), # On utilise date_vue (datetime complet)
                )
                # --- FIN DE LA MODIFICATION ---

        logger.info(f"Scan ENREGISTRÉ (QR suivi) pour QRCode {id_qrcode} depuis {client_host} ({user_agent})")

        # Redirection vers l’URL cible
        return RedirectResponse(url=qr.url, status_code=307)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur lors du scan : %s", e)
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------
# 🔹 DÉTAILS QR PAR ID
# -------------------------------------------------------------
@app.get("/qrcode/{id_qrcode}", tags=["QR Codes"])
async def details_qrcode(id_qrcode: int):
    """Retourne les informations détaillées d'un QR code"""
    qr = qrcode_service.dao.trouver_par_id(id_qrcode)  # lecture DAO
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")
    return qr.to_dict()  # objet -> dict JSON sérialisable


# -------------------------------------------------------------
# 🔹 IMAGE PNG DU QR CODE (MODIFIÉ)
# -------------------------------------------------------------
@app.get("/qrcode/{id_qrcode}/image", tags=["QR Codes"])
async def image_qrcode(id_qrcode: int):
    """Renvoie le fichier image PNG pré-généré du QR code (celui qui encode l'URL de scan)."""

    # 1. Vérifie que l'enregistrement QR existe en base
    qr = qrcode_service.dao.trouver_par_id(id_qrcode)
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")

    # 2. Construit le chemin attendu du fichier image
    #    (Basé sur la logique de votre 'QRCodeService.creer_qrc')
    file_name = f"qrcode_{id_qrcode}.png"
    file_path = os.path.join(QR_OUTPUT_DIR, file_name)

    # 3. Vérifie si le fichier image existe physiquement
    if not os.path.exists(file_path):
        logger.error(f"Image non trouvée sur le disque pour QR {id_qrcode} à {file_path}")
        raise HTTPException(status_code=404, detail="Fichier image non trouvé. (Le QR existe en base mais le fichier PNG est manquant)")

    # 4. Renvoie le fichier
    return FileResponse(file_path, media_type="image/png")


# -------------------------------------------------------------
# 🔹 STATISTIQUES D'UN QR CODE
# -------------------------------------------------------------
@app.get("/qrcode/{id_qrcode}/stats", tags=["Stats"])
async def stats_qrcode(id_qrcode: int, detail: bool = True):
    """
    Retourne les statistiques d'un QR:
    - total_vues: nombre total de vues
    - premiere_vue: date de première vue
    - derniere_vue: date de dernière vue
    - par_jour: détail par jour (si detail=true)
    - scans_recents: log des scans individuels (si detail=true)
    """
    # Vérifie que le QR existe
    qr = qrcode_service.dao.trouver_par_id(id_qrcode)
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")

    # --- MODIFIÉ : Vérifier si le QR code est suivi ---
    if qr.type is False:
        raise HTTPException(status_code=404, detail="Statistiques non disponibles pour un QR code non-suivi.")
    # --- FIN DE LA MODIFICATION ---

    with DBConnection().connection as conn:
        with conn.cursor() as cur:
            # Agrégats (Table 'statistique')
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(nombre_vue), 0) AS total_vues,
                    MIN(date_des_vues) AS premiere_vue,
                    MAX(date_des_vues) AS derniere_vue
                FROM statistique
                WHERE id_qrcode = %s
                """,
                (id_qrcode,),
            )
            agg = cur.fetchone() or {"total_vues": 0, "premiere_vue": None, "derniere_vue": None}

            result = {
                "id_qrcode": id_qrcode,
                "total_vues": int(agg["total_vues"] or 0),
                "premiere_vue": agg["premiere_vue"].isoformat() if agg["premiere_vue"] else None,
                "derniere_vue": agg["derniere_vue"].isoformat() if agg["derniere_vue"] else None,
            }

            if detail:
                # Stats par jour (Table 'statistique')
                cur.execute(
                    """
                    SELECT date_des_vues, nombre_vue
                    FROM statistique
                    WHERE id_qrcode = %s
                    ORDER BY date_des_vues ASC
                    """,
                    (id_qrcode,),
                )
                rows = cur.fetchall() or []
                result["par_jour"] = [
                    {"date": r["date_des_vues"].isoformat(), "vues": int(r["nombre_vue"])}
                    for r in rows
                ]

                # --- AJOUTÉ : Récupérer les scans récents (avec heure) ---
                # (Table 'logs_scan')
                cur.execute(
                    """
                    SELECT date_scan, client_host
                    FROM logs_scan
                    WHERE id_qrcode = %s
                    ORDER BY date_scan DESC
                    LIMIT 50
                    """, # On limite aux 50 plus récents
                    (id_qrcode,),
                )
                logs = cur.fetchall() or []
                # Ajoute la nouvelle clé "scans_recents" à la réponse JSON
                result["scans_recents"] = [
                    {"timestamp": log["date_scan"].isoformat(), "client": log["client_host"]}
                    for log in logs
                ]
                # --- FIN DE L'AJOUT ---

    return result



# -------------------------------------------------------------
# 🔹 ROUTE PAR DÉFAUT
# -------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def index():
    """Redirige vers la documentation Swagger"""
    return RedirectResponse(url="/docs")


# -------------------------------------------------------------
# 🔹 Lancement du serveur
# -------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    # S'assure que root_path est bien lu au démarrage
    app_root_path = os.getenv("ROOT_PATH", "") 
    logger.info(f"✅ Serveur lancé sur 0.0.0.0:{port} avec ROOT_PATH='{app_root_path}'")
    uvicorn.run(app, host="0.0.0.0", port=port, root_path=app_root_path)

