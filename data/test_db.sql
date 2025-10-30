-- Commandes pratiques:
-- Exécuter tout le fichier:

-- psql -h postgresql-495411.user-id2774 -p 5432 -U user-id2774 -d defaultdb -f data/test_db.sql
--  APPUYER SUR Q POUR QUITTER


-- dump_db.sql — Aperçu lisible des données du schéma 'projet'
SET search_path TO projet;

-- 1) Utilisateurs
SELECT
  u.id_user,
  u.nom_user
FROM utilisateur u
ORDER BY u.id_user;

-- 2) Tokens (si utilisés)
SELECT
  t.id_user,
  u.nom_user,
  t.jeton
FROM token t
JOIN utilisateur u ON u.id_user = t.id_user
ORDER BY t.id_user;

-- 3) QR codes avec propriétaire
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

-- 4) Statistiques brutes (par jour)
SELECT
  s.id_qrcode,
  q.url,
  s.date_des_vues,
  s.nombre_vue
FROM statistique s
JOIN qrcode q ON q.id_qrcode = s.id_qrcode
ORDER BY s.id_qrcode, s.date_des_vues;

-- 5) Statistiques agrégées par QR (total, première et dernière vue)
SELECT
  s.id_qrcode,
  q.url,
  COALESCE(SUM(s.nombre_vue), 0) AS total_vues,
  MIN(s.date_des_vues) AS premiere_vue,
  MAX(s.date_des_vues) AS derniere_vue
FROM statistique s
JOIN qrcode q ON q.id_qrcode = s.id_qrcode
GROUP BY s.id_qrcode, q.url
ORDER BY s.id_qrcode;
