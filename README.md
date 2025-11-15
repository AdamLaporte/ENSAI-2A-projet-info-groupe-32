# ENSAI-2A-Projet-Info-Groupe-32 (QR Code Tracking)

Ce projet est une application complète de génération et de suivi de QR codes, réalisée dans le cadre du projet informatique de 2A à l'ENSAI.

Cette application met en œuvre plusieurs concepts clés :

  - Programmation en couches (DAO, Service, View, Business\_Object)
  - Connexion à une base de données **PostgreSQL**
  - Une interface en ligne de commande (CLI) avec [inquirerPy](https://inquirerpy.readthedocs.io/en/latest/)
  - Une **API Webservice** (back-end) créée avec [FastAPI](https://fastapi.tiangolo.com/)
  - La génération de QR codes (statiques et dynamiques)
  - Le suivi statistique (scans, géolocalisation) pour les QR codes dynamiques

Elle constitue une excellente base pour des applications réelles de génération et traçabilité de QR codes.

## :arrow\_forward: Software and tools

  - [Visual Studio Code](https://code.visualstudio.com/)
  - [Python 3.13](https://www.python.org/) (ou 3.10+)
  - [Git](https://git-scm.com/)
  - Une base de données [PostgreSQL](https://www.postgresql.org/)

## :arrow\_forward: Clone the repository

  - [ ] Ouvrir VSCode
  - [ ] Ouvrir **Git Bash**
  - [ ] Cloner le dépôt
      - `git clone [URL_DE_VOTRE_DEPOT_GIT]`

### Open Folder

  - [ ] Ouvrir **Visual Studio Code**
  - [ ] File \> Open Folder
  - [ ] Sélectionner le dossier du projet (ex: `ENSAI-2A-projet-info-groupe-32`)
      - Le dossier doit être à la racine de votre Explorateur
      - :warning: Sinon, l'application ne se lancera pas.


## Project  architecture
L'application suit une architecture organisée et maintenable :

src/
├── business_object/ # Modèles métier (Qrcode, Statistique, Utilisateur, Token…)
├── dao/ # Accès aux tables PostgreSQL (psycopg2)
├── service/ # Logique métier (création, suppression, suivi)
├── utils/ # Génération QR, décorateurs, logs, reset DB
├── view/ # CLI interactive dans le terminal
├── app.py # API FastAPI
└── main.py # Point d’entrée du CLI


## Repository Files Overview

| Item | Description |
| -------------------------- | ------------------------------------------------------------------------ |
| `README.md` | Fournit les informations utiles pour présenter, installer et utiliser l'application |
| `LICENSE` | Spécifie les droits d'utilisation et les termes de la licence du dépôt |

### Configuration files

Ce dépôt contient un grand nombre de fichiers de configuration pour paramétrer les différents outils utilisés.

| Item | Description |
| -------------------------- | ------------------------------------------------------------------------ |
| `.github/workflows/ci.yml` | Workflow automatisé qui exécute des tâches prédéfinies (tests, linting...) |
| `.vscode/settings.json` | Contient les paramètres de VS Code spécifiques à ce projet |
| `.coveragerc` | Configuration pour la couverture de test |
| `.gitignore` | Liste les fichiers et dossiers qui ne doivent pas être suivis par Git |
| `logging_config.yml` | Configuration pour les logs |
| `requirements.txt` | Liste les packages Python requis pour le projet |

Vous aurez également besoin d'un fichier `.env`. Voir ci-dessous.



### Folders

| Item | Description |
| -------------------------- | ------------------------------------------------------------------------ |
| `data` | Scripts SQL contenant les jeux de données (création et peuplement) |
| `doc` | Diagrammes UML, suivi du projet, rapport d'analyse... |
| `logs` | Contient les fichiers de logs (une fois l'application lancée) |
| `src` | Dossier contenant les fichiers Python organisés en architecture en couches |

## :arrow\_forward: Install required packages

  - [ ] Dans Git Bash, lancer les commandes suivantes pour :
      - installer tous les packages du fichier `requirements.txt`
      - lister tous les packages

<!-- end list -->

```bash
pip install -r requirements.txt
pip list
```

## :arrow\_forward: Environment variables

Vous allez maintenant définir les variables d'environnement pour déclarer la base de données et l'API.

À la racine du projet :

  - [ ] Créer un fichier nommé `.env`
  - [ ] Coller et compléter les éléments ci-dessous

<!-- end list -->

```.env
# --- Configuration de la base de données ---
POSTGRES_HOST=sgbd-eleves.domensai.ecole
POSTGRES_PORT=5432
POSTGRES_DATABASE=idxxxx
POSTGRES_USER=idxxxx
POSTGRES_PASSWORD=idxxxx
POSTGRES_SCHEMA=projet

# --- Configuration de l'API FastAPI ---
# Port sur lequel le serveur uvicorn écoutera
PORT=5000

# URL de base de l'API (pour la redirection et l'affichage des images)
# Doit correspondre à l'URL où votre API est accessible
BASE_URL="http://127.0.0.1:5000"

# URL de scan (celle qui sera encodée dans le QR code suivi)
# Elle doit pointer vers votre API, sur la route /scan
SCAN_BASE_URL="http://127.0.0.1:5000/scan"

# Dossier de sortie pour les images PNG des QR codes
QRCODE_OUTPUT_DIR="static/qrcodes"
```

## :arrow\_forward: Unit tests

  - [ ] Dans Git Bash: `pytest -v`
      - ou `python -m pytest -v` si *pytest* n'a pas été ajouté au *PATH*

### TU DAO

Pour garantir que les tests sont répétables, sûrs et **n'interfèrent pas avec la base de données réelle**, nous utilisons un schéma dédié pour les tests unitaires (`projet_test_dao`).

Les tests unitaires DAO utilisent les données du fichier `data/pop_db_test.sql`.

### Test coverage

Il est également possible de générer la couverture de test en utilisant [Coverage](https://coverage.readthedocs.io/en/7.4.0/index.html).

:bulb: Le fichier `.coveragerc` peut être utilisé pour modifier les paramètres.

  - [ ] `coverage run -m pytest`
  - [ ] `coverage report -m`
  - [ ] `coverage html`
      - Télécharger et ouvrir coverage\_report/index.html

## :arrow\_forward: Launch the CLI application

Cette application fournit une interface graphique basique dans le terminal pour naviguer entre les différents menus.

  - [ ] Dans Git Bash: `python src/main.py`
  - [ ] Au premier lancement, choisir **Ré-initialiser la base de données**
      - cela appelle le programme `src/utils/reset_database.py`
      - qui exécutera lui-même les scripts SQL du dossier `data` (`init_db.sql` et `pop_db.sql`)

## :arrow\_forward: Launch the webservice (API)

L'application principale est un webservice (API).

  - [ ] `python src/app.py`

Le serveur est maintenant lancé (par défaut sur `http://127.0.0.1:5000`).

Documentation :

  - **Swagger UI (Interactif) : [http://127.0.0.1:5000/docs](https://www.google.com/search?q=http://127.0.0.1:5000/docs)**
  - **ReDoc : [http://127.0.0.1:5000/redoc](https://www.google.com/search?q=http://127.0.0.1:5000/redoc)**

### Endpoints

Exemples d'endpoints (à tester avec *Insomnia*, un navigateur, ou via l'application CLI) :

  - `GET /scan/{id_qrcode}`

      - Route principale pour le scan, enregistre la vue et redirige.

  - `POST /qrcode/`

      - **Body JSON :**
        ```json
        {
          "url": "https://www.ensai.fr",
          "id_proprietaire": "1",
          "type_qrcode": true,
          "couleur": "blue"
        }
        ```

  - `GET /qrcode/utilisateur/{id_user}`

      - Récupère tous les QR codes de l'utilisateur.

  - `GET /qrcode/{id_qrcode}/stats`

      - Récupère les statistiques d'un QR code (total, par jour, logs récents).

  - `GET /qrcode/{id_qrcode}/image`

      - Renvoie le fichier image PNG du QR code.

  - `DELETE /qrcode/{id_qrcode}?id_user=1`

      - Supprime un QR code (vérifie que `id_user` est propriétaire).

## :arrow\_forward: Logs

Le logging est initialisé dans le module `src/utils/log_init.py` :

  - Il est appelé au démarrage de l'application (`main.py`) ou du webservice (`app.py`).
  - Il utilise le fichier `logging_config.yml` pour la configuration.
      - pour changer le niveau de log :arrow\_right: tag *level*

Un décorateur a été créé dans `src/utils/log_decorator.py`.

Lorsqu'il est appliqué à une méthode, il affichera dans les logs :

  - les paramètres d'entrée
  - la sortie

Les logs peuvent être consultés dans le dossier `logs`.

## :arrow\_forward: Continuous integration (CI)

Le dépôt contient un fichier `.github/workflows/ci.yml`.

Lorsque vous *push* sur GitHub, cela déclenche un pipeline qui effectuera les étapes suivantes :

  - Création d'un conteneur à partir d'une image Ubuntu (Linux)
  - Installation de Python
  - Installation des packages requis
  - Exécution des tests unitaires (`pytest`)
  - Analyse du code avec *pylint*
      - Si le score est inférieur à 7.5, l'étape échouera

Vous pouvez vérifier la progression de ce pipeline sur la page GitHub de votre dépôt, onglet *Actions*.

## :arrow\_forward: pour exécuter les tests

  - Exécuter tous les tests du projet
    `pytest`

  - Exécuter tous les tests avec un affichage détaillé
    `pytest -v`

  - Exécuter un fichier de test spécifique
    `pytest src/tests/test_service/test_qrcode_service.py`


# Équipe projet

Ce projet a été réalisé par les élèves ingénieurs Data Scientists en deuxième année à l'ENSAI que sont:


- **KENNE YONTA Lesline Méralda**
 