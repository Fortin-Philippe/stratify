import os
import types
import contextlib
import mysql.connector
from dotenv import load_dotenv

load_dotenv(".env")

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
                   (user_name, courriel, mdp, description, estCoach)
                   VALUES (%(user_name)s, %(courriel)s, %(mdp)s, %(description)s, %(est_coach)s)""",
                utilisateur
            )
            return curseur.lastrowid
        
def obtenir_discussions(jeu, niveau):
    """Récupère toutes les discussions pour un jeu et niveau donnés"""
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                """SELECT d.*, 
                   (SELECT COUNT(*) FROM messages WHERE discussion_id = d.id) as nombre_messages
                   FROM discussions d
                   WHERE jeu = %(jeu)s AND niveau = %(niveau)s
                   ORDER BY epingle DESC, date_creation DESC""",
                {'jeu': jeu, 'niveau': niveau}
            )
            return curseur.fetchall()

def obtenir_discussion(discussion_id):
    """Récupère une discussion par son ID"""
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                "SELECT * FROM discussions WHERE id = %(id)s",
                {'id': discussion_id}
            )
            return curseur.fetchone()

def creer_discussion(discussion):
    """Crée une nouvelle discussion"""
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                """INSERT INTO discussions
                   (titre, contenu, auteur, jeu, niveau, categorie, date_creation)
                   VALUES (%(titre)s, %(contenu)s, %(auteur)s, %(jeu)s, %(niveau)s, %(categorie)s, NOW())""",
                discussion
            )
            return curseur.lastrowid

def incrementer_vues(discussion_id):
    """Incrémente le compteur de vues d'une discussion"""
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                "UPDATE discussions SET vues = vues + 1 WHERE id = %(id)s",
                {'id': discussion_id}
            )

def obtenir_messages(discussion_id):
    """Récupère tous les messages d'une discussion"""
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                """SELECT * FROM messages 
                   WHERE discussion_id = %(discussion_id)s
                   ORDER BY date_creation ASC""",
                {'discussion_id': discussion_id}
            )
            return curseur.fetchall()

def ajouter_message(message):
    """Ajoute un message à une discussion"""
    with creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute(
                """INSERT INTO messages
                   (contenu, auteur, discussion_id, date_creation)
                   VALUES (%(contenu)s, %(auteur)s, %(discussion_id)s, NOW())""",
                message
            )
            return curseur.lastrowid