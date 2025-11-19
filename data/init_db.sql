-------------------------------------------------------------------
-- NOM: init_db.sql
-- TYPE: Définition du Schéma de Données (DDL)
-- SCHÉMA CIBLE: projet
--
-- DESCRIPTION: Crée l'ensemble des tables, colonnes, contraintes et index
--              nécessaires pour l'application de suivi de QR codes.
--              Ce script est destiné à être exécuté au premier lancement
--              ou lors de la réinitialisation de l'environnement DEV/DEMO.
-------------------------------------------------------------------

SET search_path TO projet;

-- Crée le schéma s'il n'existe pas (pour la robustesse)
CREATE SCHEMA IF NOT EXISTS projet;
SET search_path TO projet;

-------------------------------------------------------------------
-- NETTOYAGE (DROP TABLES)
-- Description: Supprime toutes les tables dans l'ordre inverse des dépendances
--              (CASCADE assure la suppression des objets dépendants).
-------------------------------------------------------------------
DROP TABLE IF EXISTS logs_scan CASCADE;
DROP TABLE IF EXISTS statistique CASCADE;
DROP TABLE IF EXISTS qrcode CASCADE;
DROP TABLE IF EXISTS token CASCADE;
DROP TABLE IF EXISTS utilisateur CASCADE;

-------------------------------------------------------------------
-- TABLE: utilisateur (Gestion des comptes utilisateurs)
-- Description: Stocke les informations de base des utilisateurs de l'application.
-- Colonnes:
--   - id_user: Identifiant unique (Clé Primaire, Auto-incrémenté)
--   - nom_user: Login de l'utilisateur (unique)
--   - mdp: Mot de passe haché
-------------------------------------------------------------------
CREATE TABLE utilisateur (
  id_user SERIAL PRIMARY KEY,
  nom_user TEXT NOT NULL,
  mdp TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_utilisateur_nom_user ON utilisateur(nom_user);

-------------------------------------------------------------------
-- TABLE: token (Gestion des sessions d'authentification)
-- Description: Stocke le jeton de session temporaire associé à un utilisateur.
-- Colonnes:
--   - id_token: Clé Primaire du jeton (Auto-incrémenté)
--   - id_user: Clé Étrangère vers l'utilisateur
--   - jeton: Chaîne de caractères unique et sécurisée
--   - date_expiration: Horodatage de l'expiration du jeton
-------------------------------------------------------------------
CREATE TABLE token (
  id_token SERIAL PRIMARY KEY, 
  id_user INT NOT NULL,
  jeton TEXT NOT NULL,
  date_expiration TIMESTAMPTZ,
  FOREIGN KEY (id_user) REFERENCES utilisateur(id_user) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_token_jeton ON token(jeton);
CREATE INDEX IF NOT EXISTS idx_token_id_user ON token(id_user);

-------------------------------------------------------------------
-- TABLE: qrcode (Gestion des QR codes créés)
-- Description: Stocke les métadonnées de chaque QR code généré.
-- Colonnes:
--   - id_qrcode: Identifiant unique (Clé Primaire, Auto-incrémenté)
--   - url: URL de destination finale
--   - id_proprietaire: Clé Étrangère vers l'utilisateur créateur
--   - date_creation: Date et heure de création (par défaut: NOW())
--   - type_qrcode: Booléen (TRUE = suivi/dynamique, FALSE = statique)
--   - couleur: Code couleur de personnalisation
--   - logo: Chemin/nom du fichier logo incrusté
-------------------------------------------------------------------
CREATE TABLE qrcode (
  id_qrcode SERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  id_proprietaire INT NOT NULL,
  date_creation TIMESTAMPTZ DEFAULT NOW(),
  type_qrcode BOOLEAN,
  couleur TEXT,
  logo TEXT,
  FOREIGN KEY (id_proprietaire) REFERENCES utilisateur(id_user) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_qrcode_id_proprietaire ON qrcode(id_proprietaire);

-------------------------------------------------------------------
-- TABLE: statistique (Compteurs de vues agrégées par jour)
-- Description: Enregistre le nombre de scans par jour pour un QR code donné.
-- Colonnes:
--   - id_stat: Clé Primaire (Auto-incrémenté)
--   - id_qrcode: Clé Étrangère vers le QR code
--   - nombre_vue: Compteur de vues pour la journée (>= 0)
--   - date_des_vues: Date unique de l'enregistrement statistique
-- Contraintes:
--   - uq_stat_qrcode_date: Garantit une seule entrée par QR code et par jour (pour UPSERT).
-------------------------------------------------------------------
CREATE TABLE statistique (
  id_stat SERIAL PRIMARY KEY,
  id_qrcode INT NOT NULL,
  nombre_vue INT DEFAULT 0 CHECK (nombre_vue >= 0),
  date_des_vues DATE NOT NULL,
  FOREIGN KEY (id_qrcode) REFERENCES qrcode(id_qrcode) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_stat_id_qrcode ON statistique(id_qrcode);

CREATE UNIQUE INDEX IF NOT EXISTS uq_stat_qrcode_date ON statistique(id_qrcode, date_des_vues);

-------------------------------------------------------------------
-- TABLE: logs_scan (Journal détaillé des scans individuels)
-- Description: Conserve le journal détaillé de chaque scan (pour les statistiques fines).
-- Colonnes:
--   - id_scan: Clé Primaire (Auto-incrémenté)
--   - id_qrcode: Clé Étrangère vers le QR code scanné
--   - client_host: Adresse IP/Hôte du client
--   - user_agent: Navigateur/appareil du client
--   - date_scan: Date et heure précises du scan (par défaut: NOW())
--   - referer: URL de la page de provenance
--   - accept_language: Langue du client
--   - geo_country/region/city: Informations de géolocalisation de l'IP
-------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS logs_scan (
  id_scan SERIAL PRIMARY KEY,
  id_qrcode INT NOT NULL REFERENCES qrcode(id_qrcode) ON DELETE CASCADE,
  client_host TEXT,
  user_agent TEXT,
  date_scan TIMESTAMPTZ DEFAULT NOW(),
  referer TEXT,
  accept_language TEXT,
  geo_country TEXT,
  geo_region TEXT,
  geo_city TEXT
);
CREATE INDEX IF NOT EXISTS idx_logs_scan_id_qrcode ON logs_scan(id_qrcode);