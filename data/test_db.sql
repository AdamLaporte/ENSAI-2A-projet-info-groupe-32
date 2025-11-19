-------------------------------------------------------------------
-- NOM: test_db.sql
-- TYPE: Script d'Inspection de Données (Data Inspection Script)
-- SCHÉMA CIBLE: projet
--
-- DESCRIPTION: Fournit un ensemble de requêtes SELECT pour vérifier 
--              l'état et le contenu des tables principales de l'application 
--              (utilisateurs, tokens, QR codes, statistiques, logs)
--              après le peuplement (ex: par pop_db.sql).
--
-- UTILISATION: À exécuter via psql pour une vérification manuelle des données.
-------------------------------------------------------------------

-- Commandes pratiques:
-- Exécuter tout le fichier:

-- psql -h postgresql-495411.user-id2774 -p 5432 -U user-id2774 -d defaultdb -f data/test_db.sql
--  APPUYER SUR Q POUR QUITTER


SET search_path TO projet;

-------------------------------------------------------------------
-- REQUÊTE 1: Utilisateurs
-- Description: Liste tous les utilisateurs par ordre d'ID.
-- Tables interrogées: utilisateur
-- Colonnes retournées: id_user, nom_user
-------------------------------------------------------------------
SELECT
  u.id_user,
  u.nom_user
FROM utilisateur u
ORDER BY u.id_user;

-------------------------------------------------------------------
-- REQUÊTE 2: Tokens actifs
-- Description: Affiche les jetons d'authentification existants, avec le nom de l'utilisateur associé.
-- Tables interrogées: token, utilisateur
-- Colonnes retournées: id_user, nom_user, jeton
-------------------------------------------------------------------
SELECT
  t.id_user,
  u.nom_user,
  t.jeton
FROM token t
JOIN utilisateur u ON u.id_user = t.id_user
ORDER BY t.id_user;

-------------------------------------------------------------------
-- REQUÊTE 3: Détails des QR codes
-- Description: Affiche tous les QR codes, y compris leur propriétaire, type, et personnalisation.
-- Tables interrogées: qrcode, utilisateur
-- Colonnes retournées: id_qrcode, url, id_proprietaire, proprietaire, date_creation, type_qrcode, couleur, logo
-------------------------------------------------------------------
SELECT
  q.id_qrcode,
  q.url,
  q.id_proprietaire,
  u.nom_user AS proprietaire,
  q.date_creation,
  q.type_qrcode,
  q.couleur,
  q.logo
FROM qrcode q
JOIN utilisateur u ON u.id_user = q.id_proprietaire
ORDER BY q.id_qrcode;

-------------------------------------------------------------------
-- REQUÊTE 4: Statistiques brutes journalières
-- Description: Affiche l'historique des vues par jour pour chaque QR code.
-- Tables interrogées: statistique, qrcode
-- Colonnes retournées: id_qrcode, url, date_des_vues, nombre_vue
-------------------------------------------------------------------
SELECT
  s.id_qrcode,
  q.url,
  s.date_des_vues,
  s.nombre_vue
FROM statistique s
JOIN qrcode q ON q.id_qrcode = s.id_qrcode
ORDER BY s.id_qrcode, s.date_des_vues;

-------------------------------------------------------------------
-- REQUÊTE 5: Statistiques agrégées (Résumées)
-- Description: Calcule le total des vues, la première et la dernière vue, 
--              uniquement pour les QR codes de type 'suivi' (type_qrcode = TRUE).
-- Tables interrogées: statistique, qrcode
-- Colonnes retournées: id_qrcode, url, total_vues, premiere_vue, derniere_vue
-------------------------------------------------------------------
SELECT
  s.id_qrcode,
  q.url,
  COALESCE(SUM(s.nombre_vue), 0) AS total_vues,
  MIN(s.date_des_vues) AS premiere_vue,
  MAX(s.date_des_vues) AS derniere_vue
FROM statistique s
RIGHT JOIN qrcode q ON q.id_qrcode = s.id_qrcode
WHERE q.type_qrcode = TRUE
GROUP BY s.id_qrcode, q.url
ORDER BY s.id_qrcode;

-------------------------------------------------------------------
-- REQUÊTE 6: Journal détaillé des scans
-- Description: Affiche les logs de scans détaillés (y compris géo/navigateur), 
--              triés du plus récent au plus ancien.
-- Tables interrogées: logs_scan, qrcode
-- Colonnes retournées: id_scan, id_qrcode, url, date_scan, client_host, geo_city, geo_region, geo_country, user_agent, referer, accept_language
-------------------------------------------------------------------
SELECT
  l.id_scan,
  l.id_qrcode,
  q.url,
  l.date_scan,
  l.client_host,
  l.geo_city,
  l.geo_region,
  l.geo_country,
  l.user_agent,
  l.referer,
  l.accept_language
FROM logs_scan l
JOIN qrcode q ON q.id_qrcode = l.id_qrcode
ORDER BY l.date_scan DESC;