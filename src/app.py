import os
import logging
from datetime import datetime
# AJOUTÉ : Depends pour l'injection de dépendances
from fastapi import FastAPI, HTTPException, Request, Depends
# Ajout de FileResponse pour renvoyer des fichiers
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import requests # <-- AJOUTÉ POUR L'API DE GÉOLOCALISATION


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
app = FastAPI()

QR_OUTPUT_DIR = os.getenv("QRCODE_OUTPUT_DIR", "static/qrcodes")

def get_qrcode_service():
    return QRCodeService(QRCodeDao())

# --- NOUVELLE FONCTION : Helper de Géolocalisation ---
def _get_geolocation_from_ip(ip: str) -> (Optional[str], Optional[str], Optional[str]):
    """
    Appelle une API de géo-IP externe pour obtenir le pays, la région et la ville.
    Retourne (None, None, None) en cas d'échec ou d'IP privée.
    """
    # Ne pas appeler l'API pour des IP privées/locales
    #if not ip or ip == "127.0.0.1" or ip.startswith("192.168.") or ip.startswith("10."):
    #    return (None, None, None)
        
    try:
        # Utilise un timeout court pour ne pas ralentir la redirection
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city", timeout=0.5)
        response.raise_for_status() # Lève une erreur pour les statuts 4xx/5xx
        
        data = response.json()
        
        if data.get("status") == "success":
            return (
                data.get("country"),
                data.get("regionName"),
                data.get("city")
            )
        else:
            logger.warning(f"Échec de la géolocalisation pour l'IP {ip}: {data.get('message')}")
            return (None, None, None)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel à l'API de géolocalisation pour {ip}: {e}")
        return (None, None, None)
# --- FIN DE LA NOUVELLE FONCTION ---


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
async def creer_qrc(data: QRCodeCreateModel, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
    """
    Créer un QR code, l'enregistrer et renvoyer ses détails 
    incluant l'URL de l'image et l'URL de scan.
    """
    try:
        created = qrcode_service.creer_qrc(
            url=data.url,
            id_proprietaire=data.id_proprietaire,
            type_=data.type_qrcode, 
            couleur=data.couleur,
            logo=data.logo,
        ) 

        response_data = created.to_dict()
        response_data["scan_url"] = getattr(created, '_scan_url', None)
        response_data["image_url"] = getattr(created, '_image_url', None)

        return JSONResponse(content=response_data, status_code=201)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur création QR code : %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/qrcode/utilisateur/{id_user}", tags=["QR Codes"])
async def qrcodes_par_utilisateur(id_user: str, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
    """Lister tous les QR codes d’un utilisateur"""
    try:
        qrs = qrcode_service.trouver_qrc_par_id_user(id_user)
        return [q.to_dict() for q in qrs]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erreur lors du listing des QR codes pour user {id_user} : {e}")
        return [] 

@app.delete("/qrcode/{id_qrcode}", tags=["QR Codes"])
async def supprimer_qrcode(id_qrcode: int, id_user: str, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
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
async def scan_qrcode(id_qrcode: int, request: Request, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
    """
    Lorsqu'un utilisateur scanne le QR code :
    - [GÉO] Tente de géolocaliser l'IP
    - [LOG] on enregistre une statistique (date, +1) si le QR est 'suivi'
    - [REDIRECTION] puis on redirige vers l'URL réelle
    """
    try:
        qr = qrcode_service.dao.trouver_par_id(id_qrcode)
        if not qr:
            raise HTTPException(status_code=404, detail="QR code introuvable")

        if qr.type is False:
            logger.info(f"Scan NON enregistré (QR non-suivi) pour QRCode {id_qrcode}")
            return RedirectResponse(url=qr.url, status_code=307)

        # --- Données de la requête ---
        user_agent = request.headers.get("user-agent", "inconnu")
        client_host = request.client.host if request.client else "inconnu"
        date_vue = datetime.utcnow()
        referer = request.headers.get("referer") 
        language = request.headers.get("accept-language")

        # --- AJOUT : Appel de l'API de GÉOLOCALISATION ---
        geo_country, geo_region, geo_city = _get_geolocation_from_ip(client_host)
        # --- FIN DE L'AJOUT ---

        # Enregistrement en BDD
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                # 1. Incrémenter la table agrégée
                cur.execute(
                    """
                    INSERT INTO statistique (id_qrcode, nombre_vue, date_des_vues)
                    VALUES (%s, 1, %s)
                    ON CONFLICT (id_qrcode, date_des_vues)
                    DO UPDATE SET nombre_vue = statistique.nombre_vue + 1;
                    """,
                    (id_qrcode, date_vue.date()),
                )
                
                # 2. Insérer le log détaillé (avec les données GÉO)
                cur.execute(
                    """
                    INSERT INTO logs_scan (
                        id_qrcode, client_host, user_agent, date_scan, referer, accept_language,
                        geo_country, geo_region, geo_city
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        id_qrcode, client_host, user_agent, date_vue, referer, language,
                        geo_country, geo_region, geo_city # <-- AJOUTÉ
                    )
                )

        logger.info(f"Scan ENREGISTRÉ (QR suivi) pour QRCode {id_qrcode} depuis {client_host} ({geo_city}, {geo_country})")

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
async def details_qrcode(id_qrcode: int, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
    """Retourne les informations détaillées d'un QR code"""
    qr = qrcode_service.dao.trouver_par_id(id_qrcode) 
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")
    return qr.to_dict() 


# -------------------------------------------------------------
# 🔹 IMAGE PNG DU QR CODE (MODIFIÉ)
# -------------------------------------------------------------
@app.get("/qrcode/{id_qrcode}/image", tags=["QR Codes"])
async def image_qrcode(id_qrcode: int, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
    """Renvoie le fichier image PNG pré-généré du QR code (celui qui encode l'URL de scan)."""

    qr = qrcode_service.dao.trouver_par_id(id_qrcode)
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")

    file_name = f"qrcode_{id_qrcode}.png"
    file_path = os.path.join(QR_OUTPUT_DIR, file_name)

    if not os.path.exists(file_path):
        logger.error(f"Image non trouvée sur le disque pour QR {id_qrcode} à {file_path}")
        raise HTTPException(status_code=404, detail="Fichier image non trouvé. (Le QR existe en base mais le fichier PNG est manquant)")

    return FileResponse(file_path, media_type="image/png")


# -------------------------------------------------------------
# 🔹 STATISTIQUES D'UN QR CODE
# -------------------------------------------------------------
@app.get("/qrcode/{id_qrcode}/stats", tags=["Stats"])
async def stats_qrcode(id_qrcode: int, detail: bool = True, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
    """
    Retourne les statistiques d'un QR:
    - total_vues: nombre total de vues
    - ...et plus
    """
    qr = qrcode_service.dao.trouver_par_id(id_qrcode)
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")

    if qr.type is False:
        raise HTTPException(status_code=404, detail="Statistiques non disponibles pour un QR code non-suivi.")

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

                # (Table 'logs_scan')
                # --- MODIFICATION ICI : AJOUT DES COLONNES GÉO ---
                cur.execute(
                    """
                    SELECT date_scan, client_host, user_agent, referer, accept_language,
                           geo_country, geo_region, geo_city
                    FROM logs_scan
                    WHERE id_qrcode = %s
                    ORDER BY date_scan DESC
                    LIMIT 50
                    """, 
                    (id_qrcode,),
                )
                logs = cur.fetchall() or []
                result["scans_recents"] = [
                    {
                        "timestamp": log["date_scan"].isoformat(), 
                        "client": log["client_host"],
                        "user_agent": log["user_agent"],
                        "referer": log["referer"],
                        "language": log["accept_language"],
                        # --- AJOUTS GÉO ---
                        "geo_country": log["geo_country"],
                        "geo_region": log["geo_region"],
                        "geo_city": log["geo_city"]
                    }
                    for log in logs
                ]
                # --- FIN DE LA MODIFICATION ---

    return result



# -------------------------------------------------------------
# 🔹 ROUTE PAR DÉFAUT
# -------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def index():
    """Redirige vers la documentation Swagger"""
    return RedirectResponse(url="./docs")


# -------------------------------------------------------------
# 🔹 Lancement du serveur
# -------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    app_root_path = os.getenv("ROOT_PATH", "") 
    logger.info(f"✅ Serveur lancé sur 0.0.0.0:{port} avec ROOT_PATH='{app_root_path}'")
    uvicorn.run(app, host="0.0.0.0", port=port, root_path=app_root_path)