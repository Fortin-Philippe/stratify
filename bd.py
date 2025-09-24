from pymongo import MongoClient

MONGO_URI = "mongodb+srv://phfor002_db_user:YjTbyYIKddYhyHj7@bd-stratify.nhgylm6.mongodb.net/?retryWrites=true&w=majority&appName=BD-Stratify"

client = MongoClient(MONGO_URI)
db = client["Stratify"]
utilisateurs = db["utilisateurs"]

def ajouter_utilisateur(utilisateur):
    return utilisateurs.insert_one(utilisateur)