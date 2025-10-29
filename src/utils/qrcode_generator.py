# utils/qrcode_generator.py
import os
from io import BytesIO
from typing import Optional
from datetime import datetime
import uuid
from PIL import Image
import qrcode
from qrcode.constants import ERROR_CORRECT_H

# optionnel: SVG support via segno 
try:
    import segno  # type: ignore
    HAS_SEGNO = True
except Exception:
    HAS_SEGNO = False


DEFAULT_OUTPUT_DIR = os.getenv("QRCODE_OUTPUT_DIR", "static/qrcodes")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")  # used for exposing saved files via HTTP


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def generate_qr_png_bytes(
    payload: str,
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white",
    logo_path: Optional[str] = None,
    logo_scale: float = 0.2,
) -> bytes:
    """
    Génère un PNG (bytes) contenant le QR pour `payload`.
    - logo_path: chemin vers image (png/jpg) à coller au centre (optionnel).
    - logo_scale: fraction de la dimension totale réservée au logo (0.2 = 20%).
    """
    # 1) créer le QR
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=box_size, border=border)
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    # 2) ajouter logo si présent
    if logo_path:
        try:
            logo = Image.open(logo_path).convert("RGBA")
            img_w, img_h = img.size
            max_logo_w = int(img_w * logo_scale)
            max_logo_h = int(img_h * logo_scale)
            logo.thumbnail((max_logo_w, max_logo_h), Image.LANCZOS)
            lx = (img_w - logo.width) // 2
            ly = (img_h - logo.height) // 2
            img.paste(logo, (lx, ly), logo)
        except Exception:
            # Ne pas interrompre la génération si logo invalide — retournera QR sans logo
            pass

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_qr_svg_bytes(payload: str, scale: int = 4) -> Optional[bytes]:
    """
    Génère un SVG (bytes) si 'segno' est disponible. Sinon renvoie None.
    """
    if not HAS_SEGNO:
        return None
    qr = segno.make(payload, error='h')
    buf = BytesIO()
    qr.save(buf, kind='svg', scale=scale)
    return buf.getvalue()


def save_bytes_to_file(content: bytes, out_dir: str, filename: Optional[str] = None) -> str:
    """
    Sauvegarde bytes en fichier dans out_dir. Retourne le chemin absolu du fichier.
    """
    _ensure_dir(out_dir)
    if filename is None:
        filename = datetime.utcnow().strftime("%Y%m%d%H%M%S-") + uuid.uuid4().hex + ".png"
    path = os.path.join(out_dir, filename)
    with open(path, "wb") as f:
        f.write(content)
    return os.path.abspath(path)


def generate_and_save_qr_png(
    tracking_url: str,
    out_dir: Optional[str] = None,
    filename: Optional[str] = None,
    fill_color: str = "black",
    back_color: str = "white",
    logo_path: Optional[str] = None,
    logo_scale: float = 0.2,
    box_size: int = 10,
    border: int = 4,
) -> str:
    """
    Génère le QR pour `tracking_url`, sauve en PNG dans out_dir, retourne le path.
    """
    out_dir = out_dir or DEFAULT_OUTPUT_DIR
    png_bytes = generate_qr_png_bytes(
        payload=tracking_url,
        box_size=box_size,
        border=border,
        fill_color=fill_color,
        back_color=back_color,
        logo_path=logo_path,
        logo_scale=logo_scale,
    )
    saved = save_bytes_to_file(png_bytes, out_dir, filename)
    return saved


def filepath_to_public_url(filepath: str, base_url: Optional[str] = None) -> str:
    """
    Si les fichiers sont servis statiquement sous BASE_URL, transforme file path -> URL.
    Ex: filepath = /app/static/qrcodes/2025...png -> base_url + '/static/qrcodes/...png'
    Cela suppose que le répertoire DEFAULT_OUTPUT_DIR est exposé sous '/static/qrcodes'.
    """
    base_url = base_url or BASE_URL
    # find the relative portion assuming DEFAULT_OUTPUT_DIR is relative to project root
    rel = os.path.relpath(filepath, start=os.getcwd())
    # sanitize windows sep
    rel = rel.replace(os.path.sep, "/")
    return f"{base_url}/{rel}"
