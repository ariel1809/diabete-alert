from flask import Flask, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

# Charger les variables d'environnement pour l'URI de MongoDB
# MONGO_USER = os.getenv("MONGO_USER")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = os.getenv("MONGO_DB")

# Encoder le mot de passe si nécessaire
# MONGO_PASSWORD = MONGO_PASSWORD.replace("#", "%23")  # Exemple pour encoder '#'

# Construire l'URI MongoDB
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
print(MONGO_URI)

# Initialiser le client MongoDB
client = MongoClient(MONGO_URI)

# Accéder à la base de données
db = client.get_database()

@app.route('/test-connexion')
def test_connexion():
    try:
        # Tester la connexion en listant les collections
        collections = db.list_collection_names()
        return jsonify({"success": True, "collections": collections}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
