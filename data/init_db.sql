-- Utilisateur
DROP TABLE IF EXISTS utilisateur CASCADE;
CREATE TABLE utilisateur (
  id_user SERIAL PRIMARY KEY,
  mdp TEXT NOT NULL
);

-- Token
DROP TABLE IF EXISTS token CASCADE;
CREATE TABLE token (
  id_token SERIAL PRIMARY KEY,
  id_user INT NOT NULL,
  jeton TEXT NOT NULL,
  UNIQUE (jeton),
  FOREIGN KEY (id_user) REFERENCES utilisateur(id_user) ON DELETE CASCADE
);
CREATE INDEX idx_token_id_user ON token(id_user);

-- QRCode
DROP TABLE IF EXISTS qrcode CASCADE;
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
CREATE INDEX idx_qrcode_id_proprietaire ON qrcode(id_proprietaire);

-- Statistique
DROP TABLE IF EXISTS statistique CASCADE;
CREATE TABLE statistique (
  id_stat SERIAL PRIMARY KEY,
  id_qrcode INT NOT NULL,
  nombre_vue INT DEFAULT 0 CHECK (nombre_vue >= 0),
  date_des_vues DATE,
  -- option: vues JSONB,
  FOREIGN KEY (id_qrcode) REFERENCES qrcode(id_qrcode) ON DELETE CASCADE
);
CREATE INDEX idx_stat_id_qrcode ON statistique(id_qrcode);
