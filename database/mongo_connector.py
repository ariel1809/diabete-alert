from flask_pymongo import PyMongo

mongo = PyMongo()  # Initialise l'objet PyMongo

def init_db(app):
    """
    Initialise la connexion à la base de données MongoDB.
    """
    mongo.init_app(app)
    return mongo