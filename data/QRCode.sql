CREATE TABLE QRCode (
    id_qrcode SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    id_proprietaire INT NOT NULL,
    date_creation DATE DEFAULT CURRENT_DATE,
    type BOOLEAN,              
    couleur TEXT,
    logo TEXT,
    FOREIGN KEY (id_proprietaire) REFERENCES Utilisateur(id_user) ON DELETE CASCADE
);