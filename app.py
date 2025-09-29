from flask import Flask, render_template, redirect, request, url_for, session, flash
from bd import creer_connexion
from accueil import bp as accueil_bp
import os

app = Flask(__name__)
app.register_blueprint(accueil_bp)

app.secret_key = "cletemporaire"

@app.route('/creer-utilisateur', methods=['GET', 'POST'])
def form_utilisateur():
    if request.method == 'POST':
        nom_utilisateur = request.form['nom_utilisateur']
        courriel = request.form['courriel']
        mdp = request.form['mdp']
        description = request.form.get('description', None)
        est_coach = bool(request.form.get('est_coach'))

        utilisateur = {
            "user_name": nom_utilisateur,
            "courriel": courriel,
            "mdp": mdp,
            "description": description,
            "est_coach": est_coach
        }

        from bd import ajouter_utilisateur
        ajouter_utilisateur(utilisateur)

        return redirect(url_for('home'))
    else:
        return render_template("form-utilisateur.jinja")


@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Tu dois être connecté.", "danger")
        return redirect(url_for("home"))

    with creer_connexion() as conn:
        with conn.get_curseur() as cursor:
            cursor.execute("SELECT * FROM Utilisateur WHERE id=%s", (session["user_id"],))
            user = cursor.fetchone()

    return render_template("profile.jinja", user=user)

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        flash("Tu dois être connecté.", "danger")
        return redirect(url_for("home"))

    with creer_connexion() as conn:
        with conn.get_curseur() as cursor:
            cursor.execute("SELECT * FROM Utilisateur WHERE id=%s", (session["user_id"],))
            user = cursor.fetchone()

            if request.method == "POST":
                username = request.form["username"]
                description = request.form["description"]
                lstJeux = request.form["lstJeux"]

                image_file = user["image"]
                if "image" in request.files:
                    file = request.files["image"]
                    if file and file.filename != "":
                        upload_folder = os.path.join("static", "img", "profiles")
                        os.makedirs(upload_folder, exist_ok=True)

                        filename = f"user{session['user_id']}_{file.filename}"
                        image_path = os.path.join(upload_folder, filename)
                        file.save(image_path)

                        image_file = f"img/profiles/{filename}"

                cursor.execute("""
                    UPDATE Utilisateur
                    SET user_name=%s, description=%s, lstJeux=%s, image=%s
                    WHERE id=%s
                """, (username, description, lstJeux, image_file, session["user_id"]))

    flash("Profil mis à jour avec succès ✅", "success")
    return redirect(url_for("profile"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Déconnecté ✅", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
