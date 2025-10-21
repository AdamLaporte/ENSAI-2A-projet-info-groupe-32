-- pop_db_test.sql
SET search_path TO projet_test_dao;

BEGIN;

-- Utilisateur
INSERT INTO utilisateur (nom_user, mdp) VALUES
  ('test_u1', 'test_u1'),
  ('test_u2', 'test_u2'),
  ('test_u3', 'test_u3');

-- Token (u1,u2 ont un jeton; u3 aucun)
INSERT INTO token (id_user, jeton)
SELECT u.id_user, t.jeton
FROM (VALUES
  ('test_u1', 'tok_test_u1'),
  ('test_u2', 'tok_test_u2')
) AS t(nom_user, jeton)
JOIN utilisateur u ON u.nom_user = t.nom_user;

-- QRCode
INSERT INTO qrcode (url, id_proprietaire, type_qrcode, couleur, logo, date_creation)
SELECT q.url, u.id_user, q.type_qrcode, q.couleur, q.logo, q.date_creation
FROM (VALUES
  ('https://t.local/u1/a', 'test_u1', TRUE,  'black',  NULL,      DATE '2025-10-01'),
  ('https://t.local/u2/b', 'test_u2', FALSE, 'red',    'lg2.png', DATE '2025-10-02'),
  ('https://t.local/u3/c', 'test_u3', TRUE,  'blue',   'lg3.png', DATE '2025-10-03')
) AS q(url, nom_user, type_qrcode, couleur, logo, date_creation)
JOIN utilisateur u ON u.nom_user = q.nom_user;

-- Statistique
WITH urls AS (SELECT id_qrcode, url FROM qrcode)
INSERT INTO statistique (id_qrcode, nombre_vue, date_des_vues)
SELECT u.id_qrcode, s.nombre_vue, s.date_des_vues
FROM (VALUES
  ('https://t.local/u1/a',  0,  DATE '2025-10-01'),
  ('https://t.local/u1/a',  5,  DATE '2025-10-02'),
  ('https://t.local/u2/b',  3,  DATE '2025-10-02'),
  ('https://t.local/u3/c', 10,  DATE '2025-10-03')
) AS s(url, nombre_vue, date_des_vues)
JOIN urls u ON u.url = s.url;

COMMIT;
