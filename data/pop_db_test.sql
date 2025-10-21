-- pop_db_test.sql
-- Jeu de données minimal et déterministe pour les tests DAO
-- Ajuste le schéma si nécessaire (ex: projet_test_dao)
SET search_path TO projet_test_dao;

BEGIN;

-----------------------------------------------------
-- Utilisateur
-----------------------------------------------------
INSERT INTO utilisateur (mdp) VALUES
  ('test_u1'),
  ('test_u2'),
  ('test_u3');

-----------------------------------------------------
-- Token (référence utilisateur.id_user)
-----------------------------------------------------
INSERT INTO token (id_user, token) VALUES
  (1, 'tok_test_u1'),
  (2, 'tok_test_u2');
-- L’utilisateur 3 n’a pas de token pour couvrir le cas "aucun token"

-----------------------------------------------------
-- QRCode (référence utilisateur.id_user via id_proprietaire)
-----------------------------------------------------
INSERT INTO qrcode (url, id_proprietaire, type, couleur, logo, date_creation) VALUES
  ('https://t.local/u1/a', 1, TRUE,  'black',  NULL,      DATE '2025-10-01'),
  ('https://t.local/u2/b', 2, FALSE, 'red',    'lg2.png', DATE '2025-10-02'),
  ('https://t.local/u3/c', 3, TRUE,  'blue',   'lg3.png', DATE '2025-10-03');

-----------------------------------------------------
-- Statistique (référence qrcode.id_qrcode)
-----------------------------------------------------
INSERT INTO statistique (id_qrcode, nombre_vue, date_des, vues) VALUES
  (1, 0,  DATE '2025-10-01', 'init'),
  (1, 5,  DATE '2025-10-02', 'web:mobile'),
  (2, 3,  DATE '2025-10-02', 'web:desktop'),
  (3, 10, DATE '2025-10-03', 'social');

COMMIT;
