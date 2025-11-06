import logging

from utils.singleton import Singleton
from utils.log_decorator import log
from datetime import date, datetime
from dao.db_connection import DBConnection

from business_object.statistique import Statistique


class StatistiqueDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Statistiques dans la base de données"""

    @log
    def creer_statistique(self, statistique) -> bool:
        """Création d'une statistique dans la base de données

        Parameters
        ----------
        statistique : Statistique

        Returns
        -------
        created : bool
            True si la création est un succès
            False sinon
        """

        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO statistique(id_qrcode, id_stat, nombre_vue, date_des_vues)
                        VALUES (%(id_qrcode)s, %(id_stat)s, %(nombre_vue)s, %(date_des_vues)s)
                        RETURNING id_stat;
                        """,
                        {
                            "id_qrcode": statistique.id_qrcode,
                            "id_stat": statistique.id_stat,
                            "nombre_vue": statistique.nombre_vue,
                            "date_des_vues": statistique.date_des_vues,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        created = False
        if res:
            created = True

        return created

    @log
    def trouver_par_id_stat(self, id_stat) -> Statistique:
        """Trouver une statistique grâce à l'id de la stat

        Parameters
        ----------
        id_stat : int
            identifiant de la statistique

        Returns
        -------
        statistique : Statistique
            renvoie la statistique correspondante
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT *
                          FROM statistique
                         WHERE id_stat = %(id_stat)s;
                        """,
                        {"id_stat": id_stat},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        statistique = None
        if res:
            statistique = Statistique(
                id_qrcode=res["id_qrcode"],
                id_stat=res["id_stat"],
                nombre_vue=res["nombre_vue"],
                date_des_vues=res["date_des_vues"],
            )

        return statistique

    @log
    def lister_toutes(self) -> list[Statistique]:
        """Lister toutes les statistiques présentes dans la base de données"""

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT *
                        FROM statistique;
                        """
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        stats_dict = {}

        for row in res:
            key = (row["id_qrcode"], row["id_stat"])

            # Conversion de la date SQL → objet datetime.date
            if isinstance(row["date_des_vues"], str):
                vue_date = datetime.strptime(row["date_des_vues"], "%Y-%m-%d").date()
            else:
                vue_date = row["date_des_vues"]

            if key not in stats_dict:
                stats_dict[key] = {
                    "id_qrcode": row["id_qrcode"],
                    "id_stat": row["id_stat"],
                    "nombre_vue": row["nombre_vue"],
                    "date_des_vues": [vue_date],
                }
            else:
                stats_dict[key]["date_des_vues"].append(vue_date)
                stats_dict[key]["nombre_vue"] += row["nombre_vue"]

        liste_statistiques = []
        for data in stats_dict.values():
            statistique = Statistique(
                id_qrcode=data["id_qrcode"],
                id_stat=data["id_stat"],
                nombre_vue=data["nombre_vue"],
                date_des_vues=data["date_des_vues"],
            )
            liste_statistiques.append(statistique)

        return liste_statistiques


    @log
    def modifier_statistique(self, statistique) -> bool:
        """Modification d'une statistique dans la base de données

        Parameters
        ----------
        statistique : Statistique

        Returns
        -------
        modified : bool
            True si la modification est un succès
            False sinon
        """

        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE statistique
                           SET nombre_vue = %(nombre_vue)s,
                               date_des_vues = %(date_des_vues)s
                         WHERE id_qrcode = %(id_qrcode)s;
                        """,
                        {
                            "nombre_vue": statistique.nombre_vue,
                            "date_des_vues": statistique.date_des_vues,
                            "id_qrcode": statistique.id_qrcode,
                        },
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)

        return res == 1

    @log
    def supprimer(self, statistique) -> bool:
        """Suppression d'une statistique dans la base de données

        Parameters
        ----------
        statistique : Statistique
            statistique à supprimer

        Returns
        -------
        deleted : bool
            True si la suppression a réussi
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM statistique
                         WHERE id_qrcode = %(id_qrcode)s;
                        """,
                        {"id_qrcode": statistique.id_qrcode},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
            raise

        return res > 0