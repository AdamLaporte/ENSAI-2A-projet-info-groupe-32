import os
import logging
import requests
from dotenv import load_dotenv
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timezone 
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from dao.qrcode_dao import QRCodeDao
from service.statistique_service import StatistiqueService
from service.log_scan_service import LogScanService
from dao.log_scan_dao import LogScanDao
from service.qrcode_service import QRCodeService, QRCodeNotFoundError, UnauthorizedError
from service.utilisateur_service import UtilisateurService
from service.token_service import TokenService
from dao.token_dao import TokenDao


# Logging de base
logging.basicConfig(level=logging.INFO, format="%(asctime=s) - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Initialisation de l'application ---
root_path = os.getenv("ROOT_PATH", "")
app = FastAPI()

QR_OUTPUT_DIR = os.getenv("QRCODE_OUTPUT_DIR", "static/qrcodes")

# -------------------------------------------------------------
# 🔹 INJECTION DE DÉPENDANCES (SERVICES)
# -------------------------------------------------------------


def get_qrcode_service():
    return QRCodeService(QRCodeDao())


def get_statistique_service():
    return StatistiqueService()


def get_log_scan_service():
    return LogScanService(LogScanDao())


def get_utilisateur_service():
    return UtilisateurService()


def get_token_service():
    return TokenService()


def get_token_dao():
    return TokenDao()


# --- NOUVELLE FONCTION : Helper de Géolocalisation ---
def _get_geolocation_from_ip(ip: str) -> (Optional[str], Optional[str], Optional[str]):
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city",
            timeout=0.5,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            return (data.get("country"), data.get("regionName"), data.get("city"))
        else:
            logger.warning(f"Échec de la géolocalisation pour l'IP {ip}: {data.get('message')}")
            return (None, None, None)
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel à l'API de géolocalisation pour {ip}: {e}")
        return (None, None, None)


# --- Modèles d’entrée pour l’API ---


class UserCreateModel(BaseModel):
    nom_user: str = Field(..., min_length=1)
    mdp: str = Field(..., min_length=5)


class QRCodeCreateModel(BaseModel):
    url: str
    id_proprietaire: str
    type_qrcode: Optional[bool] = True
    couleur: Optional[str] = "black"
    logo: Optional[str] = None


class QRCodeUpdateModel(BaseModel):
    url: Optional[str] = None
    type_qrcode: Optional[bool] = None
    couleur: Optional[str] = None
    logo: Optional[str] = None


# -------------------------------------------------------------
# 🔹 NOUVEAU : Configuration de la sécurité (OAuth2)
# -------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Impossible de valider les identifiants",
    headers={"WWW-Authenticate": "Bearer"},
)


async def verifier_token_valide(
    token_str: str = Depends(oauth2_scheme),
    token_service: TokenService = Depends(get_token_service),
) -> int:
    """
    Dépendance FastAPI pour valider un token.
    Appelée automatiquement pour chaque route protégée.
    """
    try:
        token_obj = token_service.trouver_par_jeton(token_str)

        if not token_obj or not token_service.est_valide_token(token_obj):
            logger.warning(f"Token expiré ou invalide reçu : {token_str[:10]}...")
            raise credentials_exception

        return int(token_obj.id_user)
    except Exception as e:
        logger.error(f"Erreur validation token : {e}")
        raise credentials_exception


# -------------------------------------------------------------
# 🔹 NOUVEAU : Route de Login
# -------------------------------------------------------------
@app.post("/login", tags=["Authentification"])
async def login_pour_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UtilisateurService = Depends(get_utilisateur_service),
    token_service: TokenService = Depends(get_token_service),
):
    """
    Prend un nom_user (username) et mdp (password)
    et retourne un token Bearer s'ils sont valides.
    """
    user = user_service.se_connecter(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = token_service.creer_token(user.id_user)
    if not token:
        raise HTTPException(status_code=500, detail="Impossible de créer le token")

    return {"access_token": token.jeton, "token_type": "bearer"}


# -------------------------------------------------------------
# 🔹 NOUVEAU : Route d'Inscription (Publique)
# -------------------------------------------------------------
@app.post("/register", tags=["Authentification"], status_code=status.HTTP_201_CREATED)
async def register_user(
    data: UserCreateModel,
    user_service: UtilisateurService = Depends(get_utilisateur_service),
):
    """
    Crée un nouveau compte utilisateur.
    Route publique.
    """
    try:
        if user_service.nom_user_deja_utilise(data.nom_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le nom d'utilisateur '{data.nom_user}' est déjà utilisé.",
            )

        user = user_service.creer_user(data.nom_user, data.mdp)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La création du compte a échoué pour une raison inconnue.",
            )

        return {
            "id_user": user.id_user,
            "nom_user": user.nom_user,
            "message": "Compte créé avec succès.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erreur lors de l'inscription de {data.nom_user}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# 🔹 ROUTES QR CODE CRUD (MAINTENANT PROTÉGÉES)
# -------------------------------------------------------------
@app.post("/qrcode/", tags=["QR Codes"])
async def creer_qrc(
    data: QRCodeCreateModel,
    qrcode_service: QRCodeService = Depends(get_qrcode_service),
    current_user_id: int = Depends(verifier_token_valide),
):
    """
    Créer un QR code (authentification requise).
    """
    try:
        data.id_proprietaire = str(current_user_id)

        created = qrcode_service.creer_qrc(
            url=data.url,
            id_proprietaire=data.id_proprietaire,
            type_qrcode=data.type_qrcode,
            couleur=data.couleur,
            logo=data.logo,
        )

        response_data = created.to_dict()
        response_data["scan_url"] = getattr(created, "_scan_url", None)
        response_data["image_url"] = getattr(created, "_image_url", None)

        return JSONResponse(content=response_data, status_code=201)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur création QR code : %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/qrcode/utilisateur/me", tags=["QR Codes"])
async def qrcodes_par_utilisateur_connecte(
    current_user_id: int = Depends(verifier_token_valide),
    qrcode_service: QRCodeService = Depends(get_qrcode_service),
):
    """Lister tous les QR codes de l'utilisateur authentifié."""
    try:
        qrs = qrcode_service.trouver_qrc_par_id_user(str(current_user_id))
        return [q.to_dict() for q in qrs]
    except Exception as e:
        logger.exception(f"Erreur lors du listing des QR codes pour user {current_user_id} : {e}")
        return []


@app.delete("/qrcode/{id_qrcode}", tags=["QR Codes"])
async def supprimer_qrcode(
    id_qrcode: int,
    current_user_id: int = Depends(verifier_token_valide),
    qrcode_service: QRCodeService = Depends(get_qrcode_service),
):
    """Supprimer un QR code (seulement par le propriétaire authentifié)"""
    try:
        ok = qrcode_service.supprimer_qrc(id_qrcode, str(current_user_id))
        if not ok:
            raise HTTPException(status_code=500, detail="Erreur lors de la suppression")
        return {"success": True}
    except (QRCodeNotFoundError, UnauthorizedError) as e:
        status_code = 404 if isinstance(e, QRCodeNotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur suppression QR code : %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/qrcode/{id_qrcode}", tags=["QR Codes"])
async def modifier_qrcode(
    id_qrcode: int,
    data: QRCodeUpdateModel,
    current_user_id: int = Depends(verifier_token_valide),
    qrcode_service: QRCodeService = Depends(get_qrcode_service),
):
    """Modifier un QR code (seulement par le propriétaire authentifié)."""
    try:
        updated = qrcode_service.modifier_qrc(
            id_qrcode=id_qrcode,
            id_user=str(current_user_id),
            url=data.url,
            type_qrcode=data.type_qrcode,
            couleur=data.couleur,
            logo=data.logo,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Mise à jour échouée")

        return updated.to_dict()

    except QRCodeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError:
        raise HTTPException(status_code=403, detail="Non autorisé")
    except Exception as e:
        logger.exception("Erreur modification QR code : %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# 🔹 ROUTE SCAN (Publique, pas de token requis)
# -------------------------------------------------------------
@app.get("/scan/{id_qrcode}", include_in_schema=True, tags=["Scan"])
async def scan_qrcode(
    id_qrcode: int,
    request: Request,
    qrcode_service: QRCodeService = Depends(get_qrcode_service),
    stat_service: StatistiqueService = Depends(get_statistique_service),
    log_service: LogScanService = Depends(get_log_scan_service),
):
    """
    Route publique pour le scan.
    (fonctionnement inchangé)
    """
    try:
        qr = qrcode_service.trouver_qrc_par_id(id_qrcode)
        if not qr:
            raise HTTPException(status_code=404, detail="QR code introuvable")

        if qr.type_qrcode is False:
            logger.info(f"Scan NON enregistré (QR non-suivi) pour QRCode {id_qrcode}")
            return RedirectResponse(url=qr.url, status_code=307)

        user_agent = request.headers.get("user-agent", "inconnu")
        client_host = request.headers.get("x-forwarded-for")
        if client_host:
            client_host = client_host.split(",")[0].strip()
        else:
            client_host = request.client.host if request.client else "inconnu"
        date_vue = datetime.now(timezone.utc)
        referer = request.headers.get("referer")
        language = request.headers.get("accept-language")

        geo_country, geo_region, geo_city = _get_geolocation_from_ip(client_host)

        stat_service.enregistrer_vue(id_qrcode, date_vue.date())

        log_service.enregistrer_log(
            id_qrcode=id_qrcode,
            client_host=client_host,
            user_agent=user_agent,
            referer=referer,
            accept_language=language,
            geo_country=geo_country,
            geo_region=geo_region,
            geo_city=geo_city,
        )

        logger.info(
            f"Scan ENREGISTRÉ (QR suivi) pour QRCode {id_qrcode} depuis {client_host} ({geo_city}, {geo_country})"
        )

        destination_url = qr.url
        if not destination_url.startswith("http://") and not destination_url.startswith("https://"):
            destination_url = f"http://{destination_url}"

        return RedirectResponse(url=destination_url, status_code=307)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur lors du scan : %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# 🔹 DÉTAILS QR PAR ID (Publique ou Protégée ?)
# -------------------------------------------------------------
@app.get("/qrcode/{id_qrcode}", tags=["QR Codes"])
async def details_qrcode(
    id_qrcode: int, qrcode_service: QRCodeService = Depends(get_qrcode_service)
):
    """Retourne les informations détaillées d'un QR code (Publique)"""
    qr = qrcode_service.trouver_qrc_par_id(id_qrcode)
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")
    return qr.to_dict()


# -------------------------------------------------------------
# 🔹 IMAGE PNG DU QR CODE (Publique)
# -------------------------------------------------------------
@app.get("/qrcode/{id_qrcode}/image", tags=["QR Codes"])
async def image_qrcode(id_qrcode: int, qrcode_service: QRCodeService = Depends(get_qrcode_service)):
    """Renvoie le fichier image PNG pré-généré du QR code (Publique)"""
    qr = qrcode_service.trouver_qrc_par_id(id_qrcode)
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")
    file_name = f"qrcode_{id_qrcode}.png"
    file_path = os.path.join(QR_OUTPUT_DIR, file_name)
    if not os.path.exists(file_path):
        logger.error(f"Image non trouvée sur le disque pour QR {id_qrcode} à {file_path}")
        raise HTTPException(status_code=404, detail="Fichier image non trouvé.")
    return FileResponse(file_path, media_type="image/png")


# -------------------------------------------------------------
# 🔹 STATISTIQUES D'UN QR CODE (PROTÉGÉ)
# -------------------------------------------------------------
@app.get("/qrcode/{id_qrcode}/stats", tags=["Stats"])
async def stats_qrcode(
    id_qrcode: int,
    current_user_id: int = Depends(verifier_token_valide),
    detail: bool = True,
    qrcode_service: QRCodeService = Depends(get_qrcode_service),
    stat_service: StatistiqueService = Depends(get_statistique_service),
):
    """
    Retourne les statistiques d'un QR (authentification requise).
    Vérifie également que l'utilisateur est propriétaire.
    """
    qr = qrcode_service.trouver_qrc_par_id(id_qrcode)
    if not qr:
        raise HTTPException(status_code=404, detail="QR code introuvable")

    if str(qr.id_proprietaire) != str(current_user_id):
        raise HTTPException(
            status_code=403, detail="Accès non autorisé aux statistiques de ce QR code"
        )

    if qr.type_qrcode is False:
        raise HTTPException(
            status_code=404,
            detail="Statistiques non disponibles pour un QR code non-suivi.",
        )

    try:
        result = stat_service.get_statistiques_qr_code(id_qrcode, detail)
        return result
    except Exception as e:
        logger.exception(f"Erreur inattendue lors de la récupération des stats : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur serveur lors de la récupération des statistiques.",
        )


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
    logger.info(f"Serveur lancé sur 0.0.0.0:{port} avec ROOT_PATH='{app_root_path}'")
    uvicorn.run(app, host="0.0.0.0", port=port, root_path=app_root_path)
