from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from bd import creer_connexion

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------- ROUTE DE BASE --------
@app.route("/")
def accueil():
    return render_template("accueil.jinja")


# --- Déconnexion ---
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Déconnecté ✅", "success")
    return redirect(url_for("accueil"))

# --- Page profil ---
@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Tu dois être connecté.", "danger")
        return redirect(url_for("login"))

    with creer_connexion() as conn:
        with conn.get_curseur() as cursor:
            cursor.execute("SELECT * FROM Utilisateur WHERE id=%s", (session["user_id"],))
            user = cursor.fetchone()

    return render_template("profile.jinja", user=user)

# --- Modifier profil ---
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        flash("Tu dois être connecté.", "danger")
        return redirect(url_for("login"))

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
                        filename = file.filename
                        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                        file.save(image_path)
                        image_file = f"static/uploads/{filename}"

                cursor.execute("""
                    UPDATE Utilisateur
                    SET user_name=%s, description=%s, lstJeux=%s, image=%s
                    WHERE id=%s
                """, (username, description, lstJeux, image_file, session["user_id"]))

    flash("Profil mis à jour avec succès ✅", "success")
    return redirect(url_for("profile"))

if __name__ == "__main__":
    app.run(debug=True)
