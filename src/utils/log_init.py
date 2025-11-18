import os
import logging
import logging.config
import yaml


def initialiser_logs(nom):
    """Initialiser les logs à partir du fichier de config"""

    os.makedirs("logs", exist_ok=True)

    stream = open("logging_config.yml", encoding="utf-8")
    config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)

    logging.info("-" * 50)
    logging.info(f"Lancement {nom}                           ")
    logging.info("-" * 50)
