# fichier test_utilisateur.py

from business_object.utilisateur import Utilisateur
from service.utilisateur_service import UtilisateurService

# Mock simple pour remplacer UtilisateurDao
class FakeUtilisateurDao:
    def __init__(self):
        self.utilisateurs = []

    def creer_user(self, utilisateur):
        self.utilisateurs.append(utilisateur)
        return True

    def lister_tous(self):
        return list(self.utilisateurs)

    def trouver_par_id_user(self, id_user):
        for u in self.utilisateurs:
            if u.id_user == id_user:
                return u
        return None

    def modifier_user(self, utilisateur):
        for i, u in enumerate(self.utilisateurs):
            if u.id_user == utilisateur.id_user:
                self.utilisateurs[i] = utilisateur
                return True
        return False

    def supprimer(self, utilisateur):
        if utilisateur in self.utilisateurs:
            self.utilisateurs.remove(utilisateur)
            return True
        return False

    def se_connecter(self, id_user, mdp):
        for u in self.utilisateurs:
            if u.id_user == id_user and u.mdp == mdp:
                return u
        return None


# --- Tests ---
if __name__ == "__main__":
    # On remplace temporairement le vrai DAO par notre Fake
    from service import utilisateur_service
    utilisateur_service.UtilisateurDao = FakeUtilisateurDao

    # Initialisation du service
    service = UtilisateurService()
    service._dao = FakeUtilisateurDao()

    print("=== Test création ===")
    u1 = service.creer_user("alice", "motdepasse123")
    u2 = service.creer_user("bob", "superpass")

    print("Créés :", u1, u2)

    print("\n=== Test liste ===")
    for u in service.lister_tous():
        print(u)

    print("\n=== Test trouver_par_id_user ===")
    print(service.trouver_par_id_user("alice"))

    print("\n=== Test suppression ===")
    service.supprimer(u1)
    for u in service.lister_tous():
        print(u)
