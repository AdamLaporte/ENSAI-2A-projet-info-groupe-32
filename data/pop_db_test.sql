-------------------------------------------------------------------
-- SCRIPT DE PEUPLEMENT DE LA BASE DE TESTS (pop_db_test.sql)
--
-- Objectif: Fournir un jeu de données minimal et cohérent pour l'exécution 
-- des tests unitaires et d'intégration (DAO/Services) sur le schéma 
-- 'projet_test_dao'.
--
-- Prérequis: Le schéma 'projet_test_dao' doit avoir été créé et initialisé
-- avec le DDL (Data Definition Language) des tables.
-------------------------------------------------------------------
SET search_path TO projet_test_dao;

BEGIN;

-------------------------------------------------------------------
-- INSERTION DES UTILISATEURS
-- Description: Crée trois utilisateurs de test avec des noms prévisibles.
-- Tables affectées: utilisateur
-- Données insérées: test_u1, test_u2, test_u3
-------------------------------------------------------------------
INSERT INTO utilisateur (nom_user, mdp) VALUES
  ('test_u1', 'test_u1'),
  ('test_u2', 'test_u2'),
  ('test_u3', 'test_u3');

-------------------------------------------------------------------
-- INSERTION DES TOKENS
-- Description: Crée un token pour les utilisateurs 'test_u1' et 'test_u2'.
--              'test_u3' est laissé sans token pour tester l'accès non authentifié.
-- Tables affectées: token
-- Données insérées: 2 tokens
-------------------------------------------------------------------
INSERT INTO token (id_user, jeton)
SELECT u.id_user, t.jeton
FROM (VALUES
  ('test_u1', 'tok_test_u1'),
  ('test_u2', 'tok_test_u2')
) AS t(nom_user, jeton)
JOIN utilisateur u ON u.nom_user = t.nom_user;

-------------------------------------------------------------------
-- INSERTION DES QRCODES
-- Description: Crée trois QR codes: un suivi (u1), un non-suivi (u2), et un suivi (u3).
-- Tables affectées: qrcode
-- Données insérées: 3 QR codes
-- Remarques: id_qrcode est auto-incrémenté (1, 2, 3)
-------------------------------------------------------------------
INSERT INTO qrcode (url, id_proprietaire, type_qrcode, couleur, logo, date_creation)
SELECT q.url, u.id_user, q.type_qrcode, q.couleur, q.logo, q.date_creation
FROM (VALUES
  ('https://t.local/u1/a', 'test_u1', TRUE,  'black',  NULL,      DATE '2025-10-01'), -- id_qrcode = 1 (Suivi)
  ('https://t.local/u2/b', 'test_u2', FALSE, 'red',    'lg2.png', DATE '2025-10-02'), -- id_qrcode = 2 (Non-suivi)
  ('https://t.local/u3/c', 'test_u3', TRUE,  'blue',   'lg3.png', DATE '2025-10-03')  -- id_qrcode = 3 (Suivi)
) AS q(url, nom_user, type_qrcode, couleur, logo, date_creation)
JOIN utilisateur u ON u.nom_user = q.nom_user;

-------------------------------------------------------------------
-- INSERTION DES STATISTIQUES AGRÉGÉES (PAR JOUR)
-- Description: Initialise les compteurs de vues journaliers pour les QR codes.
-- Tables affectées: statistique
-- Données insérées: 4 entrées
-------------------------------------------------------------------
WITH urls AS (SELECT id_qrcode, url FROM qrcode)
INSERT INTO statistique (id_qrcode, nombre_vue, date_des_vues)
SELECT u.id_qrcode, s.nombre_vue, s.date_des_vues
FROM (VALUES
  ('https://t.local/u1/a',  0,  DATE '2025-10-01'), -- QR #1: 0 vues le 1/10
  ('https://t.local/u1/a',  5,  DATE '2025-10-02'), -- QR #1: 5 vues le 2/10
  ('https://t.local/u2/b',  3,  DATE '2025-10-02'), -- QR #2: 3 vues le 2/10 (pour s'assurer que ça ne compte pas si non-suivi)
  ('https://t.local/u3/c', 10,  DATE '2025-10-03') -- QR #3: 10 vues le 3/10
) AS s(url, nombre_vue, date_des_vues)
JOIN urls u ON u.url = s.url;

-------------------------------------------------------------------
-- INSERTION DES LOGS DE SCANS DÉTAILLÉS
-- Description: Ajoute des entrées individuelles à la table de logs (avec Géo/IP)
-- Tables affectées: logs_scan
-- Données insérées: 2 logs pour le QR code #1
-------------------------------------------------------------------
WITH urls AS (SELECT id_qrcode, url FROM qrcode)
INSERT INTO logs_scan (id_qrcode, client_host, user_agent, date_scan, referer, accept_language, geo_country, geo_region, geo_city)
SELECT u.id_qrcode, l.client_host, l.user_agent, l.date_scan, l.referer, l.lang, l.geo_country, l.geo_region, l.geo_city
FROM (VALUES
  ('https://t.local/u1/a', '192.168.1.10', 'Mozilla/5.0 (iPhone...)', TIMESTAMPTZ '2025-10-04 08:15:30Z', NULL, 'fr-FR,fr;q=0.9', 'France', 'Bretagne', 'Rennes'),
  ('https://t.local/u1/a', '10.0.0.5',     'Mozilla/5.0 (Android...)', TIMESTAMPTZ '2025-10-04 14:45:01Z', 'https://google.com/', 'en-US,en;q=0.8', 'United States', 'California', 'Mountain View')
) AS l(url, client_host, user_agent, date_scan, referer, lang, geo_country, geo_region, geo_city)
JOIN urls u ON u.url = l.url;

COMMIT;