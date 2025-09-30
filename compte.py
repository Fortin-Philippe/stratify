import re
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, session
import bd

bp_compte = Blueprint('compte', __name__)

@bp_compte.route('/creer-utilisateur', methods=['GET', 'POST'])
def form_utilisateur():
    erreurs={}
    if request.method == 'POST':
        nom_utilisateur = request.form['nom_utilisateur'].strip()
        courriel = request.form['courriel'].strip()
        mdp = request.form['mdp'].strip()
        mdp_confirmation = request.form['mdp_confirmation'].strip()
        description = request.form.get('description', None)
        if request.form.get('est_coach') is True:
            est_coach = 1
        else:
            est_coach = 0
        est_connecte = 0

        if len(nom_utilisateur)<4 or len(nom_utilisateur)>60:
            erreurs['nom_utilisateur']= "Le nom doit contenir entre 4 et 60 caractères."
        if  not re.match(r"[^@]+@[^@]+\.[^@]+", courriel):
            erreurs['courriel']="Veuillez entrer un courriel valide."
        if len(mdp) < 3:
            erreurs['mdp'] = "Le mot de passe doit avoir au moins 3 caractères."
        if mdp != mdp_confirmation:
            erreurs['mdp_confirmation'] ="Les mots de passe ne correspondent pas."

        if erreurs:
            return render_template('form-utilisateur.jinja', erreurs =erreurs)
        utilisateur = {
            "nom_utilisateur": nom_utilisateur,
            "courriel": courriel,
            "mdp": hacher_mdp(mdp),
            "description": description,
            "est_coach": est_coach,
            "est_connecte": est_connecte
        }

        bd.ajouter_utilisateur(utilisateur)

        return redirect(url_for('home'))
    else:
         return render_template("form-utilisateur.jinja", erreurs = erreurs)

@bp_compte.route('/connexion', methods=['GET', 'POST'])
def connexion():
    erreurs = {}
    if request.method == 'POST':
        courriel = request.form['courriel'].strip()
        mdp = request.form['mdp'].strip()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", courriel):
            erreurs['courriel'] = "Veuillez entrer un courriel valide."
        else:
            utilisateur = bd.connecter_utilisateur(courriel, hacher_mdp(mdp))
            if utilisateur:
                session.permanent = True
                session['nom_utilisateur'] = utilisateur['nom_utilisateur']
                session['est_coach'] = utilisateur['est_coach']
                session['est_connecte'] = 1
                return redirect('/')
            else:
                erreurs['connexion'] = "Le courriel ou le mot de passe est invalide."

    return render_template('connexion.jinja', erreurs=erreurs)


def hacher_mdp(mdp):
    """Fonction qui hache un mot de passe"""
    return hashlib.sha512(mdp.encode()).hexdigest()