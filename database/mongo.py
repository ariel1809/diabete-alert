from flask_pymongo import PyMongo

# Création de l'objet PyMongo
mongo = PyMongo()

def init_db(app):
    """
    Initialise MongoDB avec l'application Flask.
    """
    try:
        mongo.init_app(app)  # Lier l'application Flask à l'objet PyMongo
        print("MongoDB initialisé avec URI :", app.config.get('MONGO_URI'))
    except Exception as e:
        print("Erreur d'initialisation de MongoDB :", e)
