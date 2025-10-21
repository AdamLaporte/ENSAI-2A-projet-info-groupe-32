-- pop_db.sql
-- Ajuste si besoin le schéma cible (ex: projet, projet_test_dao, etc.)
SET search_path TO projet;

BEGIN;

-- 1) Utilisateur
INSERT INTO utilisateur (mdp) VALUES
  ('azerty'),
  ('1234'),
  ('ensai2025'),
  ('pikachu'),
  ('admin');

-- 2) Token (référence utilisateur.id_user)
-- Si tu imposes un token unique par utilisateur, tu peux ajouter UNIQUE(id_user) dans le DDL.
INSERT INTO token (id_user, jeton) VALUES
  (1, 'tok_u1_a1b2c3'),
  (2, 'tok_u2_d4e5f6'),
  (3, 'tok_u3_g7h8i9'),
  (4, 'tok_u4_j1k2l3'),
  (5, 'tok_u5_m4n5o6');

-- 3) QRCode (référence utilisateur.id_user via id_proprietaire)
-- date_creation a un DEFAULT CURRENT_DATE, on laisse donc à défaut.
-- type est BOOLEAN: TRUE pour dynamique, FALSE pour statique (exemple).
INSERT INTO qrcode (url, id_proprietaire, type_qrcode, couleur, logo) VALUES
  ('https://exemple.org/u1/bienvenue', 1, TRUE,  'black',  'logo1.png'),
  ('https://exemple.org/u2/offre',     2, FALSE, 'red',    'logo2.png'),
  ('https://exemple.org/u3/profil',    3, TRUE,  'blue',   'logo3.png'),
  ('https://exemple.org/u4/contact',   4, FALSE, 'green',  'logo4.png'),
  ('https://exemple.org/u5/aide',      5, TRUE,  'purple', 'logo5.png');

-- 4) Statistique (référence qrcode.id_qrcode)
-- Exemple: agrégat journalier (date_des) + compteur (nombre_vue).
-- La colonne vues est TEXT: on met un résumé libre; remplace-la par JSONB si tu structures des détails.
INSERT INTO statistique (id_qrcode, nombre_vue, date_des_vues) VALUES
  (1,  15, DATE '2025-10-01'),
  (1,  22, DATE '2025-10-02'),
  (2,   5, DATE '2025-10-01'),
  (2,   7, DATE '2025-10-03'),
  (3,  30, DATE '2025-10-01'),
  (3,  12, DATE '2025-10-02'),
  (4,   0, DATE '2025-10-01'),
  (4,   9, DATE '2025-10-04'),
  (5, 100, DATE '2025-10-01'),
  (5,  42, DATE '2025-10-05');

COMMIT;
