````markdown
# QR Code Tracking Project - Group 32

A comprehensive application for generating, managing, and tracking QR codes using Python (FastAPI) and PostgreSQL.

## Installation & Setup

### 1. Install Dependencies
Ensure Python 3.13+ is installed, then run:
```bash
pip install -r requirements.txt
````

### 2\. Environment Configuration

Create a `.env` file at the project root and configure your database credentials:

```ini
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_db_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_SCHEMA=projet

# API Configuration
PORT=5000
BASE_URL="link that give you onyxia for the port: ex : [https://user-id2774-358651-user.user.lab.sspcloud.fr](https://user-id2774-358651-user.user.lab.sspcloud.fr)"
SCAN_BASE_URL="same link but with /scan at the end : ex : [https://user-id2774-358651-user.user.lab.sspcloud.fr/scan](https://user-id2774-358651-user.user.lab.sspcloud.fr/scan)"
QRCODE_OUTPUT_DIR=static/qrcodes
```

## How to Run

### 1\. Command-Line Interface (CLI)

The application provides a terminal-based interface (CLI) to interact with the system, manage the database, and handle QR codes.

To launch the CLI:

```bash
python src/main.py
```

**Key Features available in the CLI:**

  * **Database Initialization:**

      * Select **"Ré-initialiser la base de données"** on the first run. This will create the schema, tables, and populate the database with demo data (users, tokens, sample QR codes).

  * **Authentication:**

      * **"Créer un compte"**: Register a new user (calls the API).
      * **"Se connecter"**: Log in to access private features.

  * **User Menu (Once logged in):**

      * **Create QR Codes**: Generate new QR codes. You can choose between **Static** (direct link) or **Tracked** (dynamic link with stats), and customize the color or add a logo.
      * **My QR Codes**: List all QR codes associated with your account.
      * **Statistics**: For tracked QR codes, view detailed analytics including total views, dates, and recent scan logs (Device, IP, Location).
      * **Management**: Modify destination URLs or delete existing QR codes.

### 2\. Launch the API Server

To start the backend webservice (required for the CLI to work properly for auth and tracking):

```bash
python src/app.py
```

The server will start on the BASE\_URL defined in your `.env`.

  * **Interactive Docs:** `[BASE_URL]/docs` (e.g., `https://.../docs`).

## Testing

To run unit tests (using a dedicated test schema):

```bash
pytest
```

## Team

Adam LAPORTE, Ahmed BEIJI, Lesline Méralda KENNE YONTA, Maytena LABINSKY, Louis ROUX.
