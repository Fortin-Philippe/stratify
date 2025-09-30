import os
import types
import contextlib
import mysql.connector
from dotenv import load_dotenv

load_dotenv("/home/philfortin1/Stratify/.env")

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
                   (nom_utilisateur, courriel, mdp, description, est_coach, est_connecte)
                   VALUES (%(nom_utilisateur)s, %(courriel)s, %(mdp)s, %(description)s, %(est_coach)s, %(est_connecte)s)""",
                utilisateur
            )
            return curseur.lastrowid

def connecter_utilisateur(courriel, mdp):
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                "SELECT * FROM utilisateur WHERE courriel = %(courriel)s AND mdp =%(mdp)s",
                {
                    "courriel" : courriel,
                    "mdp" : mdp
                })
            utilisateur = curseur.fetchone()
            return utilisateur