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
# MODIFIÉ : On lit le root_path ici
root_path = os.getenv("ROOT_PATH", "") 
# MODIFIÉ : On NE PASSE PAS root_path à FastAPI() pour éviter le doublement
app = FastAPI()

# --- Définir le répertoire de sortie des images (utilisé par la route /image) ---
QR_OUTPUT_DIR = os.getenv("QRCODE_OUTPUT_DIR", "static/qrcodes")


# --- MODIFIÉ : Injection de dépendances (FIX pour "connection already closed") ---
# Cette fonction crée un NOUVEAU service pour CHAQUE requête.
# Cela garantit que la connexion à la base de données est toujours fraîche.
def get_qrcode_service():
    # Le QRCodeDao() instanciera un nouveau DBConnection()
    return QRCodeService(QRCodeDao())
# --- FIN DE LA MODIFICATION ---


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
# MODIFIÉ : Utilise l'injection de dépendances
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
# MODIFIÉ : Utilise l'injection de dépendances
async def qrcodes_par_utilisateur(id_user: str, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
    """Lister tous les QR codes d’un utilisateur"""
    try:
        qrs = qrcode_service.trouver_qrc_par_id_user(id_user)
        return [q.to_dict() for q in qrs]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erreur lors du listing des QR codes pour user {id_user} : {e}")
        # Ne pas lever d'exception ici permet au client de voir une liste vide
        return [] 
        # Si vous préférez une erreur 500, décommentez la ligne suivante
        # raise HTTPException(status_code=500, detail=str(e))


@app.delete("/qrcode/{id_qrcode}", tags=["QR Codes"])
# MODIFIÉ : Utilise l'injection de dépendances
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
# MODIFIÉ : Utilise l'injection de dépendances
async def scan_qrcode(id_qrcode: int, request: Request, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
    """
    Lorsqu'un utilisateur scanne le QR code :
    - on enregistre une statistique (date, +1) si le QR est 'suivi'
    - puis on redirige vers l'URL réelle
    """
    try:
        qr = qrcode_service.dao.trouver_par_id(id_qrcode)
        if not qr:
            raise HTTPException(status_code=404, detail="QR code introuvable")

        if qr.type is False:
            logger.info(f"Scan NON enregistré (QR non-suivi) pour QRCode {id_qrcode}")
            return RedirectResponse(url=qr.url, status_code=307)

        user_agent = request.headers.get("user-agent", "inconnu")
        client_host = request.client.host if request.client else "inconnu"
        date_vue = datetime.utcnow()
        referer = request.headers.get("referer") 
        language = request.headers.get("accept-language")

        # MODIFIÉ : N'utilise plus "with DBConnection()..."
        # La connexion est gérée par le DAO/Service injecté
        # Nous devons appeler une méthode de service pour insérer les stats
        # (Vous devrez peut-être créer cette méthode dans votre service/DAO)
        
        # NOTE: Le code ci-dessous (with DBConnection) est problématique s'il utilise
        # une connexion différente de celle du DAO.
        # Idéalement, vous devriez avoir une méthode :
        # qrcode_service.enregistrer_scan(id_qrcode, date_vue, client_host, user_agent, referer, language)
        
        # Solution temporaire : utiliser une nouvelle connexion (comme avant)
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO statistique (id_qrcode, nombre_vue, date_des_vues)
                    VALUES (%s, 1, %s)
                    ON CONFLICT (id_qrcode, date_des_vues)
                    DO UPDATE SET nombre_vue = statistique.nombre_vue + 1;
                    """,
                    (id_qrcode, date_vue.date()),
                )
                cur.execute(
                    """
                    INSERT INTO logs_scan (id_qrcode, client_host, user_agent, date_scan, referer, accept_language)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (id_qrcode, client_host, user_agent, date_vue, referer, language)
                )

        logger.info(f"Scan ENREGISTRÉ (QR suivi) pour QRCode {id_qrcode} depuis {client_host} ({user_agent})")

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
# MODIFIÉ : Utilise l'injection de dépendances
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
# MODIFIÉ : Utilise l'injection de dépendances
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
# MODIFIÉ : Utilise l'injection de dépendances
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

    # MODIFIÉ : N'utilise plus "with DBConnection()..."
    # Idéalement, qrcode_service devrait avoir une méthode "get_stats(id_qrcode)"
    # En attendant, nous utilisons une nouvelle connexion ici.
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
                cur.execute(
                    """
                    SELECT date_scan, client_host
                    FROM logs_scan
                    WHERE id_qrcode = %s
                    ORDER BY date_scan DESC
                    LIMIT 50
                    """, 
                    (id_qrcode,),
                )
                logs = cur.fetchall() or []
                result["scans_recents"] = [
                    {"timestamp": log["date_scan"].isoformat(), "client": log["client_host"]}
                    for log in logs
                ]

    return result



# -------------------------------------------------------------
# 🔹 ROUTE PAR DÉFAUT
# -------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def index():
    """Redirige vers la documentation Swagger"""
    # MODIFIÉ : s'assure que /docs est relatif au root_path
    return RedirectResponse(url="./docs")


# -------------------------------------------------------------
# 🔹 Lancement du serveur
# -------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    # S'assure que root_path est bien lu au démarrage
    app_root_path = os.getenv("ROOT_PATH", "") 
    logger.info(f"✅ Serveur lancé sur 0.0.0.0:{port} avec ROOT_PATH='{app_root_path}'")
    # MODIFIÉ : On PASSE le root_path à uvicorn.run
    uvicorn.run(app, host="0.0.0.0", port=port, root_path=app_root_path)