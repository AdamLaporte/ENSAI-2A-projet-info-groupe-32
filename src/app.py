import os
import logging
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel 

# Importez uniquement le service Utilisateur
from service.utilisateur_service import UtilisateurService 
# from business_object.utilisateur import Utilisateur 

# Assurez-vous d'avoir une fonction d'initialisation des logs
# Si elle n'est pas définie, nous devons la simuler pour que le code fonctionne
try:
    from utils.log_init import initialiser_logs
except ImportError:
    def initialiser_logs(name):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.info(f"Log system initialized for: {name}")

# --- Configuration FastAPI avec ROOT_PATH ---
# Permet à Swagger UI de fonctionner derrière le proxy (/proxy/8000)
root_path = os.getenv("ROOT_PATH", "")
app = FastAPI(title="Webservice Gestion des Utilisateurs", root_path=root_path)


initialiser_logs("Webservice")

# Initialisation du service Utilisateur
utilisateur_service = UtilisateurService()


# --- Modèles Pydantic ---

# Modèle pour le service Utilisateur
class UtilisateurModel(BaseModel):
    id_user: int | None = None  # ID auto-généré (optionnel)
    nom_user: str
    mdp: str


# --- Routes Générales et Redirection ---

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Rediriger vers la documentation de l'API"""
    return RedirectResponse(url="/docs")


# --- Routes Utilisateurs ---

# 1. Route POST (Création)
@app.post("/utilisateur/", tags=["Utilisateurs"])
async def creer_utilisateur(u: UtilisateurModel):
    """Créer un utilisateur (le mot de passe est hashé par le service)"""
    logging.info(f"Création de l'utilisateur: {u.nom_user}")
    
    if utilisateur_service.nom_user_deja_utilise(u.nom_user):
        # 409 Conflict: le nom d'utilisateur existe déjà
        raise HTTPException(status_code=409, detail=f"Nom d'utilisateur '{u.nom_user}' déjà utilisé")

    utilisateur = utilisateur_service.creer_user(u.nom_user, u.mdp)
    
    if not utilisateur:
        raise HTTPException(status_code=500, detail="Erreur interne lors de la création")

    # Important: masquez le mot de passe hashé avant de renvoyer l'objet
    utilisateur.mdp = None 
    return utilisateur


# 2. Route GET (Lister tous)
@app.get("/utilisateur/", tags=["Utilisateurs"])
async def lister_tous_utilisateurs():
    """Lister tous les utilisateurs (mots de passe masqués)"""
    logging.info("Lister tous les utilisateurs")
    # Le service s'occupe déjà de masquer le MDP par défaut
    return utilisateur_service.lister_tous(inclure_mdp=False)


# 3. Route GET (Par ID)
@app.get("/utilisateur/{id_user}", tags=["Utilisateurs"])
async def utilisateur_par_id(id_user: int):
    """Trouver un utilisateur à partir de son id"""
    logging.info(f"Recherche utilisateur par ID: {id_user}")
    utilisateur = utilisateur_service.trouver_par_id_user(id_user)
    
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
    # Masquer le mot de passe hashé
    utilisateur.mdp = None 
    return utilisateur

# --- Lancement du Serveur ---

if __name__ == "__main__":
    # Récupère le port depuis l’env (PORT=8000), sinon 9876
    port = int(os.getenv("PORT", "8000"))
    
    # Le root path est géré par la variable d'environnement ROOT_PATH
    logging.info(f"Server starting with ROOT_PATH: {root_path} on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
    logging.info("Arrêt du Webservice")
