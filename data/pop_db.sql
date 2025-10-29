-- pop_db.sql (utilisateurs: raphael, adam, ilona; sites connus; couleur 'black'; pas de logo)
SET search_path TO projet;

BEGIN;

-- Nettoyage optionnel (si tu veux repartir propre)
TRUNCATE TABLE statistique RESTART IDENTITY CASCADE;
TRUNCATE TABLE qrcode RESTART IDENTITY CASCADE;
TRUNCATE TABLE token RESTART IDENTITY CASCADE;
TRUNCATE TABLE utilisateur RESTART IDENTITY CASCADE;

-- Utilisateurs
INSERT INTO utilisateur (nom_user, mdp) VALUES
  ('raphael', 'pwdraphael'),
  ('adam',    'pwdadam'),
  ('ilona',   'pwdilona');

-- Jetons (si utilisé)
INSERT INTO token (id_user, jeton)
SELECT u.id_user, t.jeton
FROM (VALUES
  ('raphael', 'tok_raphael_demo'),
  ('adam',    'tok_adam_demo'),
  ('ilona',   'tok_ilona_demo')
) AS t(nom_user, jeton)
JOIN utilisateur u ON u.nom_user = t.nom_user;

-- QR codes (nombre différent par utilisateur, couleur 'black', logo NULL)
-- raphael: 3 QR
-- adam   : 2 QR
-- ilona  : 1 QR
INSERT INTO qrcode (url, id_proprietaire, type_qrcode, couleur, logo)
SELECT q.url, u.id_user, q.type_qrcode, q.couleur, NULL::text
FROM (VALUES
  -- raphael (3)
  ('https://ensai.fr',                     'raphael', TRUE,  'black'),
  ('https://www.youtube.com/',             'raphael', TRUE,  'black'),
  ('https://fr.wikipedia.org/wiki/ENSAI',  'raphael', TRUE,  'black'),

  -- adam (2)
  ('https://github.com/',                  'adam',    TRUE,  'black'),
  ('https://www.ensae.fr/',                'adam',    FALSE, 'black'),

  -- ilona (1)
  ('https://www.insee.fr/fr/accueil',      'ilona',   TRUE,  'black')
) AS q(url, nom_user, type_qrcode, couleur)
JOIN utilisateur u ON u.nom_user = q.nom_user;

-- Statistiques journalières variées (dates d'exemple)
WITH urls AS (SELECT id_qrcode, url FROM qrcode)
INSERT INTO statistique (id_qrcode, nombre_vue, date_des_vues)
SELECT u.id_qrcode, s.nombre_vue, s.date_des_vues
FROM (VALUES
  -- raphael: ENSAI, YouTube, Wikipedia
  ('https://ensai.fr',                     DATE '2025-10-01', 14),
  ('https://ensai.fr',                     DATE '2025-10-02', 19),
  ('https://ensai.fr',                     DATE '2025-10-05',  6),

  ('https://www.youtube.com/',             DATE '2025-10-01', 28),
  ('https://www.youtube.com/',             DATE '2025-10-03', 37),
  ('https://www.youtube.com/',             DATE '2025-10-05', 31),

  ('https://fr.wikipedia.org/wiki/ENSAI',  DATE '2025-10-02',  8),
  ('https://fr.wikipedia.org/wiki/ENSAI',  DATE '2025-10-04', 15),

  -- adam: GitHub, ENSAE
  ('https://github.com/',                  DATE '2025-10-01', 12),
  ('https://github.com/',                  DATE '2025-10-02', 16),
  ('https://github.com/',                  DATE '2025-10-04',  7),

  ('https://www.ensae.fr/',                DATE '2025-10-02',  4),
  ('https://www.ensae.fr/',                DATE '2025-10-05', 11),

  -- ilona: INSEE
  ('https://www.insee.fr/fr/accueil',      DATE '2025-10-01',  5),
  ('https://www.insee.fr/fr/accueil',      DATE '2025-10-03',  3),
  ('https://www.insee.fr/fr/accueil',      DATE '2025-10-05', 10)
) AS s(url, date_des_vues, nombre_vue)
JOIN urls u ON u.url = s.url;

COMMIT;
