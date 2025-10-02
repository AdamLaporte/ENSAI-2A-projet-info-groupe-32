# Répartition des tâches pour la phase de développement

Après la phase de recherche et de compréhension des éléments techniques (API, DAO, authentification par token, gestion des accès, etc.), notre groupe a défini une organisation du travail afin de garantir une progression efficace et structurée du projet.

Nous avons choisi une répartition basée sur les **entités principales du modèle**.  
Chaque membre du groupe prend en charge l’implémentation complète d’une entité, incluant :  
- la classe métier,  
- le DAO associé,  
- le service correspondant,  
- ainsi que les tests unitaires.  

Cette approche permet de responsabiliser chaque membre, tout en gardant une cohérence globale grâce à des conventions communes définies en amont.  

## Tableau de répartition

| Membre   | Responsabilités |
|----------|-----------------|
| **Membre 1** | `Utilisateur`, `UtilisateurDAO`, `UtilisateurService`, tests associés |
| **Membre 2** | `QRCode`, `QRCodeDAO`, `QRCodeService`, tests associés |
| **Membre 3** | `Statistique`, `StatistiqueDAO`, `StatistiqueService`, tests associés |
| **Membre 4** | `Token`, `TokenDAO`, `TokenService`, tests associés |
| **Membre 5** | Mise en place de la **base de données**, définition des contraintes d’intégrité et relations, cohérence des schémas, et coordination pour assurer la concordance entre les différentes implémentations |

---

Bienqu'on n'ait pas encore assigné de partie à chacun, cela nous permet de disposer d’un périmètre clair de responsabilités, tout en participant à la réussite collective.  
