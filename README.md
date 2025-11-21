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
BASE_URL= "link that give you onyxia for the port: ex : https://user-id2774-358651-user.user.lab.sspcloud.fr"
SCAN_BASE_URL="same link but with /scan at the end : ex : https://user-id2774-358651-user.user.lab.sspcloud.fr/scan"
QRCODE_OUTPUT_DIR=static/qrcodes
```

## How to Run

### 1\. Reset Database & CLI

To initialize the database tables or use the command-line interface:

```bash
python src/main.py
```

> **Important:** On the first run, select **"Ré-initialiser la base de données"** in the menu to create the schema and populate initial data.

### 2\. Launch the API Server

To start the backend webservice:

```bash
python src/app.py
```

The server will start on the BASE_URL in the .env ex: `https://user-id2774-358651-user.user.lab.sspcloud.fr` .

  - **Interactive Docs:** ex: `https://user-id2774-358651-user.user.lab.sspcloud.fr/doc`.

## Testing

To run unit tests (using a dedicated test schema):

```bash
pytest
```

## Team

Adam LAPORTE, Ahmed BEIJI, Lesline Méralda KENNE YONTA, Maytena LABINSKY, Louis ROUX.
