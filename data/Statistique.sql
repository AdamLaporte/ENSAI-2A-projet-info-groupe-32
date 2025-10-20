CREATE TABLE Statistique (
    id_stat SERIAL PRIMARY KEY,
    id_qrcode INT NOT NULL,
    nombre_vue INT DEFAULT 0,
    date_des DATE,
    vues TEXT,  
    FOREIGN KEY (id_qrcode) REFERENCES QRCode(id_qrcode) ON DELETE CASCADE
);