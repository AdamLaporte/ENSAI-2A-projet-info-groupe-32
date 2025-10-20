CREATE TABLE Token (
    id_user INT NOT NULL,
    token TEXT NOT NULL,
    FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE
);
