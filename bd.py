import os
import types
import contextlib
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


@contextlib.contextmanager
def creer_connexion():
    conn = mysql.connector.connect(
        user=os.getenv('BD_UTILISATEUR'),
        password=os.getenv('BD_MDP'),
        host=os.getenv('BD_SERVEUR'),
        database=os.getenv('BD_NOM_SCHEMA'),
        raise_on_warnings=True
    )

    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    curseur = self.cursor(dictionary=True, buffered=True)
    try:
        yield curseur
    finally:
        curseur.close()


def ajouter_utilisateur(utilisateur):
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                """INSERT INTO utilisateur
                   (user_name, courriel, mdp, description, estCoach, lstJeux, image)
                   VALUES (%(user_name)s, %(courriel)s, %(mdp)s, %(description)s, %(est_coach)s, %(lstJeux)s, %(image)s)""",
                utilisateur
            )
            return curseur.lastrowid


def connecter_utilisateur(courriel, mdp):
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                "SELECT * FROM utilisateur WHERE courriel = %(courriel)s AND mdp = %(mdp)s",
                {"courriel": courriel, "mdp": mdp}
            )
            return curseur.fetchone()


def get_utilisateur_par_id(user_id):
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                "SELECT * FROM utilisateur WHERE id = %(id)s",
                {"id": user_id}
            )
            return curseur.fetchone()


def update_utilisateur(user_id, data):
    colonnes = ", ".join(f"{k} = %({k})s" for k in data.keys())
    data["id"] = user_id
    requete = f"UPDATE utilisateur SET {colonnes} WHERE id = %(id)s"

    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(requete, data)
