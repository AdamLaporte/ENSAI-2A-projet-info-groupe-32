-- pop_db.sql
SET search_path TO projet;

BEGIN;

-- Utilisateur
INSERT INTO utilisateur (nom_user, mdp) VALUES
  ('alice', 'azerty'),
  ('bob', '1234'),
  ('carol', 'ensai2025'),
  ('dave', 'pikachu'),
  ('admin', 'admin');

-- Token par nom_user
INSERT INTO token (id_user, jeton)
SELECT u.id_user, t.jeton
FROM (VALUES
  ('alice', 'tok_u1_a1b2c3'),
  ('bob',   'tok_u2_d4e5f6'),
  ('carol', 'tok_u3_g7h8i9'),
  ('dave',  'tok_u4_j1k2l3'),
  ('admin', 'tok_u5_m4n5o6')
) AS t(nom_user, jeton)
JOIN utilisateur u ON u.nom_user = t.nom_user;

-- QRCode
INSERT INTO qrcode (url, id_proprietaire, type_qrcode, couleur, logo)
SELECT q.url, u.id_user, q.type_qrcode, q.couleur, q.logo
FROM (VALUES
  ('https://exemple.org/u1/bienvenue', 'alice', TRUE,  'black',  'logo1.png'),
  ('https://exemple.org/u2/offre',     'bob',   FALSE, 'red',    'logo2.png'),
  ('https://exemple.org/u3/profil',    'carol', TRUE,  'blue',   'logo3.png'),
  ('https://exemple.org/u4/contact',   'dave',  FALSE, 'green',  'logo4.png'),
  ('https://exemple.org/u5/aide',      'admin', TRUE,  'purple', 'logo5.png')
) AS q(url, nom_user, type_qrcode, couleur, logo)
JOIN utilisateur u ON u.nom_user = q.nom_user;

-- Statistique
WITH urls AS (SELECT id_qrcode, url FROM qrcode)
INSERT INTO statistique (id_qrcode, nombre_vue, date_des_vues)
SELECT u.id_qrcode, s.nombre_vue, s.date_des_vues
FROM (VALUES
  ('https://exemple.org/u1/bienvenue', 15, DATE '2025-10-01'),
  ('https://exemple.org/u1/bienvenue', 22, DATE '2025-10-02'),
  ('https://exemple.org/u2/offre',      5, DATE '2025-10-01'),
  ('https://exemple.org/u2/offre',      7, DATE '2025-10-03'),
  ('https://exemple.org/u3/profil',    30, DATE '2025-10-01'),
  ('https://exemple.org/u3/profil',    12, DATE '2025-10-02'),
  ('https://exemple.org/u4/contact',    0, DATE '2025-10-01'),
  ('https://exemple.org/u4/contact',    9, DATE '2025-10-04'),
  ('https://exemple.org/u5/aide',     100, DATE '2025-10-01'),
  ('https://exemple.org/u5/aide',      42, DATE '2025-10-05')
) AS s(url, nombre_vue, date_des_vues)
JOIN urls u ON u.url = s.url;

COMMIT;
