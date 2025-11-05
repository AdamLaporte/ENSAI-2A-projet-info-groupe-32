import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

# --- Configuration pour trouver vos modules ---
# Ajoute le dossier courant au path pour que 'import service' fonctionne
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # --- Importez vos vraies classes ---
    from service.qrcode_service import QRCodeService
    from business_object.qr_code import Qrcode # Assurez-vous que ce chemin est correct
except ImportError as e:
    print(f"Erreur d'importation: {e}")
    print("Veuillez lancer ce script depuis la racine de votre projet.")
    sys.exit(1)

# --- 1. Simulation du DAO ---
print("Initialisation du Mock DAO...")
mock_dao = Mock()

# Préparez un faux objet Qrcode (ce que le DAO est censé retourner)
fake_qr_from_db = Qrcode(
    id_qrcode=123,  # L'ID est crucial
    url="https://ma-destination-finale.com",
    id_proprietaire="user-test-terminal",
    date_creation=datetime.now(),
    type=True,
    couleur="green",
    logo="logo.png"
)

# Configurez le mock : quand 'creer_qrc' est appelé, retournez notre faux objet
mock_dao.creer_qrc.return_value = fake_qr_from_db

# --- 2. Initialisation du Service avec le Faux DAO ---
service = QRCodeService(dao=mock_dao)

# --- 3. Définition du test ---

# On "patch" (remplace) les fonctions externes pour qu'elles ne s'exécutent pas
@patch('service.qrcode_service.filepath_to_public_url')
@patch('service.qrcode_service.generate_and_save_qr_png')
def run_test(mock_gen_png, mock_url_util):
    
    # Configurez ce que les fonctions patchées doivent retourner
    mock_gen_png.return_value = "static/qrcodes/fake_path_123.png"
    mock_url_util.return_value = "https://mon-site.com/static/qrcodes/fake_path_123.png"

    print("\n--- Appel de service.creer_qrc() ---")
    
    # --- Appel de la fonction à tester ---
    created_qr = service.creer_qrc(
        url="https://ma-destination-finale.com",
        id_proprietaire="user-test-terminal",
        type_=True,
        couleur="green",
        logo="logo.png"
    )
    
    print("\n--- Sortie (Objet Qrcode retourné) ---")
    print(created_qr)
    
    print("\n--- Vérification des attributs ---")
    if created_qr:
        print(f"ID: {created_qr.id_qrcode}")
        print(f"URL de destination: {created_qr.url}")
        
        print("\n--- Attributs 'internes' ajoutés par le service ---")
        try:
            # Ces attributs sont ajoutés par votre service
            print(f"URL de scan (pour le PNG): {created_qr._scan_url}")
            print(f"Chemin image (local):    {created_qr._image_path}")
            print(f"URL image (publique):    {created_qr._image_url}")
        except AttributeError as e:
            print(f"Erreur: Un attribut interne n'a pas été ajouté. {e}")
    else:
        print("Erreur: Le service n'a rien retourné.")

# --- 4. Exécution ---
if __name__ == "__main__":
    run_test()