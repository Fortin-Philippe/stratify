from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "ProjetWeb"
}

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(**db_config)

# -------- ROUTES --------
@app.route("/")
def accueil():
    return render_template("accueil.html")

# --- Page login ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Utilisateur WHERE courriel=%s AND mdp=%s",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            flash("Connecté avec succès ✅", "success")
            return redirect(url_for("profile"))
        else:
            flash("Email ou mot de passe incorrect", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

# --- Fake login pour tests ---
@app.route("/fake_login/<int:user_id>")
def fake_login(user_id):
    session["user_id"] = user_id
    flash(f"Connecté en tant qu'utilisateur {user_id}", "success")
    return redirect(url_for("profile"))

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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Utilisateur WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()
    conn.close()

    return render_template("profile.html", user=user)

# --- Modifier profil ---
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        flash("Tu dois être connecté.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Utilisateur WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()

    if request.method == "POST":
        username = request.form["username"]
        description = request.form["description"]
        lstJeux = request.form["lstJeux"]

        # Gestion image
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
        conn.commit()
        conn.close()

        flash("Profil mis à jour avec succès ✅", "success")
        return redirect(url_for("profile"))

    conn.close()
    return render_template("edit_profile.html", user=user)

# --- Lancement ---
if __name__ == "__main__":
    app.run(debug=True)
