import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # charge le .env dans os.environ

from service.qrcode_service import QRCodeService
from dao.qrcode_dao import QRCodeDao
from dao.db_connection import DBConnection

# Logging de base
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Initialisation de l'application ---
root_path = os.getenv("ROOT_PATH", "/proxy/8000")
app = FastAPI(root_path=root_path)

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
    """Créer un QR code et l'enregistrer dans la base"""
    try:
        created = qrcode_service.creer_qrc(
            url=data.url,
            id_proprietaire=data.id_proprietaire,
            type_qrcode=data.type_qrcode,
            couleur=data.couleur,
            logo=data.logo,
        )  # renvoie l'objet avec id
        return JSONResponse(content=created.to_dict(), status_code=201)
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
    - on enregistre une statistique (date, +1)
    - puis on redirige vers l'URL réelle
    """
    try:
        # Récupérer le QR cible
        qr = qrcode_service.dao.trouver_par_id(id_qrcode)
        if not qr:
            raise HTTPException(status_code=404, detail="QR code introuvable")

        # Informations client (optionnel pour logs)
        user_agent = request.headers.get("user-agent", "inconnu")
        client_host = request.client.host if request.client else "inconnu"
        date_vue = datetime.utcnow()

        # Enregistrement dans la table statistique (UPsert journalier)
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

                # Optionnel: journal détaillé si la table existe chez toi
                # cur.execute(
                #     """
                #     INSERT INTO logs_scan (id_qrcode, ip, user_agent, date_scan)
                #     VALUES (%s, %s, %s, %s);
                #     """,
                #     (id_qrcode, client_host, user_agent, date_vue),
                # )

        logger.info(f"Scan enregistré pour QRCode {id_qrcode} depuis {client_host} ({user_agent})")

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
# 🔹 IMAGE PNG DU QR CODE
# -------------------------------------------------------------
@app.get("/qrcode/{id_qrcode}/image", tags=["QR Codes"])
async def image_qrcode(id_qrcode: int, box_size: int = 10, border: int = 4):
    """Génère et renvoie l'image PNG du QR code pour l'URL associée"""
    qr = qrcode_service.dao.trouver_par_id(id_qrcode)  # lecture DAO
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")

    try:
        import qrcode
        from io import BytesIO
        from fastapi.responses import StreamingResponse

        # Construction du QR
        qrgen = qrcode.QRCode(
            version=None,  # auto
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qrgen.add_data(qr.url)
        qrgen.make(fit=True)
        img = qrgen.make_image(fill_color="black", back_color="white")

        # Export en mémoire et réponse HTTP
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except ImportError:
        raise HTTPException(status_code=500, detail="Lib 'qrcode' manquante (pip install qrcode[pil])")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    """
    # Vérifie que le QR existe
    qr = qrcode_service.dao.trouver_par_id(id_qrcode)
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")

    with DBConnection().connection as conn:
        with conn.cursor() as cur:
            # Agrégats
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
    port = int(os.getenv("PORT", 8000))
    logger.info(f"✅ Serveur lancé sur 0.0.0.0:{port} avec ROOT_PATH={root_path}")
    uvicorn.run(app, host="0.0.0.0", port=port)
