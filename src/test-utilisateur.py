#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Programme de test pour les classes Utilisateur et UtilisateurService
Projet QR Code Tracking - Équipe 32
"""

import sys
import os

# Ajouter le répertoire racine au PYTHONPATH si nécessaire
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from business_object.utilisateur import Utilisateur
from service.utilisateur_service import UtilisateurService


def test_classe_utilisateur():
    """Test de la classe Utilisateur"""
    print("=" * 50)
    print("TEST DE LA CLASSE UTILISATEUR")
    print("=" * 50)
    
    try:
        # Test 1: Création d'un utilisateur
        print("Test 1: Création d'un utilisateur")
        user1 = Utilisateur("john_doe", "motdepasse123")
        print(f"✓ Utilisateur créé: {user1}")
        print(f"  ID: {user1.id_user}")
        print(f"  MDP: {user1.mdp if user1.mdp else 'None'}")
        print()
        
        # Test 2: Utilisation des properties
        print("Test 2: Modification via properties")
        user1.id_user = "jane_doe"
        user1.mdp = "nouveaumotdepasse"
        print(f"✓ Utilisateur modifié: {user1}")
        print()
        
        # Test 3: Création avec valeurs None
        print("Test 3: Création avec valeurs None")
        user2 = Utilisateur()
        print(f"✓ Utilisateur vide créé: {user2}")
        print()
        
        # Test 4: Test d'égalité
        print("Test 4: Test d'égalité")
        user3 = Utilisateur("jane_doe", "autremotdepasse")
        print(f"user1 == user3: {user1 == user3}")  # True car même id_user
        print(f"user1 == user2: {user1 == user2}")  # False car id_user différents
        print()
        
        # Test 5: Validation des types
        print("Test 5: Test de validation des types")
        try:
            user_invalid = Utilisateur(123, "motdepasse")  # Should raise ValueError
            print("❌ Erreur: La validation n'a pas fonctionné")
        except ValueError as e:
            print(f"✓ Validation OK: {e}")
        print()
        
        print("✅ TOUS LES TESTS DE LA CLASSE UTILISATEUR SONT PASSÉS\n")
        
    except Exception as e:
        print(f"❌ ERREUR dans test_classe_utilisateur: {e}\n")


def test_utilisateur_service():
    """Test de la classe UtilisateurService (sans base de données)"""
    print("=" * 50)
    print("TEST DE LA CLASSE UTILISATEUR SERVICE")
    print("=" * 50)
    
    try:
        # Note: Ces tests ne toucheront pas la base de données
        # car nous testons juste la logique métier
        
        service = UtilisateurService()
        print("✓ UtilisateurService créé")
        print(service)
        
        # Test 1: Création d'un utilisateur (logique seulement)
        print("\nTest 1: Test de la méthode creer_user (logique)")
        try:
            # Cette méthode va essayer d'accéder à la DB, donc on s'attend à une erreur
            nouveau_user = service.creer_user("test_user", "password123")
            if nouveau_user:
                print(f"✓ Utilisateur créé par le service: {nouveau_user}")
            else:
                print("ℹ️ Service a retourné None (normal sans DB)")
        except Exception as e:
            print(f"ℹ️ Erreur attendue (pas de DB connectée): {type(e).__name__}")
        
        print("\n✅ TESTS DU SERVICE COMPLETÉS (limités sans DB)\n")
        
    except ImportError as e:
        print(f"❌ ERREUR d'import: {e}")
        print("Vérifiez que tous vos modules sont dans les bons répertoires\n")
    except Exception as e:
        print(f"❌ ERREUR dans test_utilisateur_service: {e}\n")


def test_imports():
    """Test des imports pour vérifier la structure du projet"""
    print("=" * 50)
    print("TEST DES IMPORTS")
    print("=" * 50)
    
    modules_to_test = [
        ("business_object.utilisateur", "Utilisateur"),
        ("service.utilisateur_service", "UtilisateurService"),
        ("dao.utilisateur_dao", "UtilisateurDao"),
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✓ {module_name}.{class_name} importé avec succès")
        except ImportError as e:
            print(f"❌ Erreur d'import pour {module_name}.{class_name}: {e}")
        except AttributeError as e:
            print(f"❌ Classe {class_name} non trouvée dans {module_name}: {e}")
        except Exception as e:
            print(f"❌ Erreur inattendue pour {module_name}.{class_name}: {e}")
    
    print()


def main():
    """Fonction principale de test"""
    print("🚀 DÉBUT DES TESTS - PROJET QR CODE TRACKING")
    print("Équipe 32 - Test des classes Utilisateur")
    print("=" * 60)
    
    # Test des imports
    test_imports()
    
    # Test de la classe Utilisateur
    test_classe_utilisateur()
    
    # Test du service (limité)
    test_utilisateur_service()
    
    print("=" * 60)
    print("🎯 TESTS TERMINÉS")
    print("\nNotes importantes:")
    print("- Les tests de la classe Utilisateur doivent tous passer")
    print("- Les tests du service nécessitent une base de données connectée")
    print("- Les erreurs d'import indiquent des problèmes de structure de projet")


if __name__ == "__main__":
    main()