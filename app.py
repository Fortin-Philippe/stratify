from flask import Flask, render_template, redirect, request, url_for
from bd import ajouter_utilisateur

app = Flask(__name__)

@app.route('/')
def home():
        return render_template("accueil.html")

@app.route('/creer-utilisateur', methods=['GET', 'POST'])
def form_utilisateur():
    if request.method == 'POST':
        nom_utilisateur = request.form['nom_utilisateur']
        courriel = request.form['courriel']
        mdp = request.form['mdp']
        description = request.form.get('description', None)
        est_coach = bool(request.form.get('est_coach'))

        utilisateur = {
            "nom_utilisateur": nom_utilisateur,
            "courriel": courriel,
            "mdp": mdp,
            "description": description,
            "est_coach": est_coach
        }

        ajouter_utilisateur(utilisateur)

        return redirect(url_for('home'))
    else:
         return render_template("form-utilisateur.html")

if __name__ == "__main__":
    app.run(debug=True)