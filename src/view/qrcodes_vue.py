# views/qrcode_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from service.qrcode_service import QRCodeService, QRCodeNotFoundError, UnauthorizedError
from dao.qrcode_dao import QRCodeDao
from business_object.qr_code import Qrcode

router = APIRouter(prefix="/qrcodes", tags=["QR Codes"])

# --- instancie ton vrai service ---
dao = QRCodeDao()
service = QRCodeService(dao)

# --- Schémas Pydantic pour Swagger ---


class QrcodeCreateRequest(BaseModel):
    url: str
    id_proprietaire: str
    couleur: Optional[str] = None
    logo: Optional[str] = None


class QrcodeUpdateRequest(BaseModel):
    url: Optional[str] = None
    type_: Optional[bool] = None
    couleur: Optional[str] = None
    logo: Optional[str] = None


class QrcodeResponse(BaseModel):
    id_qrcode: int
    url: str
    id_proprietaire: str
    image_url: Optional[str] = None
    couleur: Optional[str] = None
    logo: Optional[str] = None


# --- ROUTES ---

@router.post("/", response_model=QrcodeResponse)
def creer_qrcode(payload: QrcodeCreateRequest):
    """Créer un nouveau QR code."""
    try:
        qr = service.creer_qrc(
            url=payload.url,
            id_proprietaire=payload.id_proprietaire,
            couleur=payload.couleur,
            logo=payload.logo
        )
        return QrcodeResponse(
            id_qrcode=qr.id_qrcode,
            url=qr.url,
            id_proprietaire=qr.id_proprietaire,
            image_url=getattr(qr, "_image_url", None),
            couleur=qr.couleur,
            logo=qr.logo
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{id_user}", response_model=List[QrcodeResponse])
def lister_qr_user(id_user: str):
    """Lister tous les QR codes d’un utilisateur."""
    try:
        qrs = service.trouver_qrc_par_id_user(id_user)
        return [
            QrcodeResponse(
                id_qrcode=q.id_qrcode,
                url=q.url,
                id_proprietaire=q.id_proprietaire,
                image_url=getattr(q, "_image_url", None),
                couleur=q.couleur,
                logo=q.logo
            )
            for q in qrs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id_qrcode}", response_model=QrcodeResponse)
def modifier_qrcode(id_qrcode: int, id_user: str, payload: QrcodeUpdateRequest):
    """Modifier un QR code existant (si propriétaire)."""
    try:
        updated = service.modifier_qrc(
            id_qrcode=id_qrcode,
            id_user=id_user,
            url=payload.url,
            type_=payload.type_,
            couleur=payload.couleur,
            logo=payload.logo
        )
        return QrcodeResponse(
            id_qrcode=updated.id_qrcode,
            url=updated.url,
            id_proprietaire=updated.id_proprietaire,
            image_url=getattr(updated, "_image_url", None),
            couleur=updated.couleur,
            logo=updated.logo
        )
    except QRCodeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id_qrcode}")
def supprimer_qrcode(id_qrcode: int, id_user: str):
    """Supprimer un QR code si propriétaire."""
    try:
        success = service.supprimer_qrc(id_qrcode, id_user)
        return {"success": success}
    except QRCodeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
