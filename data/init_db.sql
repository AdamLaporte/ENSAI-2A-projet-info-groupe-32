-- init_db.sql (version DEV/DEMO)

SET search_path TO projet;

-- Crée le schéma si besoin (sûreté)
CREATE SCHEMA IF NOT EXISTS projet;
SET search_path TO projet;

-- Tables
DROP TABLE IF EXISTS logs_scan CASCADE;
DROP TABLE IF EXISTS statistique CASCADE;
DROP TABLE IF EXISTS qrcode CASCADE;
DROP TABLE IF EXISTS token CASCADE;
DROP TABLE IF EXISTS utilisateur CASCADE;

CREATE TABLE utilisateur (
  id_user SERIAL PRIMARY KEY,
  nom_user TEXT NOT NULL,
  mdp TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_utilisateur_nom_user ON utilisateur(nom_user);

CREATE TABLE token (
  id_user INT NOT NULL,
  jeton TEXT NOT NULL,
  FOREIGN KEY (id_user) REFERENCES utilisateur(id_user) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_token_jeton ON token(jeton);
CREATE INDEX IF NOT EXISTS idx_token_id_user ON token(id_user);

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

CREATE TABLE statistique (
  id_stat SERIAL PRIMARY KEY,
  id_qrcode INT NOT NULL,
  nombre_vue INT DEFAULT 0 CHECK (nombre_vue >= 0),
  date_des_vues DATE NOT NULL,
  FOREIGN KEY (id_qrcode) REFERENCES qrcode(id_qrcode) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_stat_id_qrcode ON statistique(id_qrcode);

-- Contrainte unique pour l'UPSERT journalier des vues
CREATE UNIQUE INDEX IF NOT EXISTS uq_stat_qrcode_date ON statistique(id_qrcode, date_des_vues);

-- Journal optionnel des scans (si tu souhaites garder le log détaillé)
-- MODIFIÉ: Renommé 'ip' en 'client_host' pour correspondre à app.py
CREATE TABLE IF NOT EXISTS logs_scan (
  id_scan SERIAL PRIMARY KEY,
  id_qrcode INT NOT NULL REFERENCES qrcode(id_qrcode) ON DELETE CASCADE,
  client_host TEXT,
  user_agent TEXT,
  date_scan TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_logs_scan_id_qrcode ON logs_scan(id_qrcode);
