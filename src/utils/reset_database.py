import os
import logging
import dotenv
from unittest import mock

from utils.log_decorator import log
from utils.singleton import Singleton
from dao.db_connection import DBConnection
from service.utilisateur_service import UtilisateurService


class ResetDatabase(metaclass=Singleton):
    """
    Réinitialisation de la base de données:
    - test_dao=False: schéma 'projet' + data/init_db.sql + data/pop_db.sql
    - test_dao=True : schéma 'projet_test_dao' + data/init_db.sql (search_path remplacé) + data/pop_db_test.sql
    """

    @log
    def lancer(self, test_dao: bool = False):
        # Sélection des fichiers
        init_path = "data/init_db.sql"
        pop_data_path = "data/pop_db_test.sql" if test_dao else "data/pop_db.sql"

        # Patch d'env pour que le code applicatif lise le bon schéma
        if test_dao:
            mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}).start()

        dotenv.load_dotenv()
        schema = os.getenv("POSTGRES_SCHEMA", "projet")

        # DROP/CREATE du schéma cible (cohérent avec POSTGRES_SCHEMA)
        create_schema = f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"

        # Lire les scripts
        with open(init_path, encoding="utf-8") as f:
            init_db_as_string = f.read()
        with open(pop_data_path, encoding="utf-8") as f:
            pop_db_as_string = f.read()

        # Remplacement dynamique du search_path dans le DDL si tests
        # Hypothèse: init_db.sql contient une ligne "SET search_path TO projet;" en tête
        if test_dao:
            init_db_as_string = init_db_as_string.replace(
                "SET search_path TO projet;",
                "SET search_path TO projet_test_dao;"
            )

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # 1) Recrée le schéma cible
                    cursor.execute(create_schema)
                    # 2) Applique le DDL
                    cursor.execute(init_db_as_string)
                    # 3) Peuple la base
                    cursor.execute(pop_db_as_string)
        except Exception as e:
            logging.info(e)
            raise

        # Post-traitement: hashage des mots de passe via le service
        utilisateur_service = UtilisateurService()
        for u in utilisateur_service.lister_tous(inclure_mdp=True):
            if u.mdp:  # si déjà hashé à la création, modifier_user renverra l'objet sans souci
                utilisateur_service.modifier_user(u)

        return True


if __name__ == "__main__":
    # Reset DEV/DEMO -> schéma 'projet'
    ResetDatabase().lancer()
    # Reset TEST -> schéma 'projet_test_dao' avec search_path remplacé en mémoire
    ResetDatabase().lancer(True)
