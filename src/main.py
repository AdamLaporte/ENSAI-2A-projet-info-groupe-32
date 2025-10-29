# main.py
from fastapi import FastAPI
from view import qrcodes_vue

app = FastAPI(
    title="API QR Codes",
    description="Service de création, modification et suppression de QR Codes.",
    version="1.0.0"
)

# --- inclure toutes les routes ---
app.include_router(qrcode_routes.router)


@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API QR Codes "}
