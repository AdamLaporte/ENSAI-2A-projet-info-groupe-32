# Répartition des tâches pour la phase de d'implémentation

Après la phase de recherche et de compréhension des éléments techniques (API, DAO, authentification par token, gestion des accès, etc.), notre groupe a défini une organisation du travail afin de garantir une progression efficace et structurée du projet.

Nous avons choisi une répartition basée sur les entités principales du modèle.  
Chaque membre du groupe prend en charge l’implémentation complète d’une entité, incluant :  
- la classe métier,  
- le DAO associé,  
- le service correspondant,  
- ainsi que les tests unitaires.  

Cette approche permet de responsabiliser chaque membre, tout en gardant une cohérence globale grâce à des conventions communes définies en amont.  

## Tableau de répartition

| Membre   | Responsabilités | Relecture |
|----------|-----------------|-----------|
| Adam | `Utilisateur`, `UtilisateurDAO`, `UtilisateurService`, tests associés | Mayténa |
| Lesline | `QRCode`, `QRCodeDAO`, `QRCodeService`, tests associés | Louis |
| Louis | `Statistique`, `StatistiqueDAO`, `StatistiqueService`, tests associés | Ahmed |
| Mayténa | `Token`, `TokenDAO`, `TokenService`, tests associés | Lesline |
| Ahmed | Mise en place de la **base de données**, définition des contraintes d’intégrité et relations, cohérence des schémas, et coordination pour assurer la concordance entre les différentes implémentations | Adam |

---
 
