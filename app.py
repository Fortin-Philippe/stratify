from flask import Flask, render_template
from compte import bp_compte
from accueil import bp as acceuil_bp
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)
app.register_blueprint(bp_compte)

app.register_blueprint(acceuil_bp)
@app.route('/')
def home():
    return render_template("accueil.jinja")

if __name__ == "__main__":
    app.run(debug=True)