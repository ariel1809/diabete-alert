# from flask_pymongo import PyMongo
#
# # Création de l'objet PyMongo
# mongo = PyMongo()
#
# def init_db(app):
#     """
#     Initialise MongoDB avec l'application Flask.
#     """
#     try:
#         mongo.init_app(app)  # Lier l'application Flask à l'objet PyMongo
#         print("MongoDB initialisé avec URI :", app.config.get('MONGO_URI'))
#     except Exception as e:
#         print("Erreur d'initialisation de MongoDB :", e)


from flask_sqlalchemy import SQLAlchemy

# Création de l'objet SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Initialise PostgreSQL avec l'application Flask.
    """
    try:
        # Lier l'application Flask à l'objet SQLAlchemy
        db.init_app(app)
        with app.app_context():
            db.create_all()  # Crée les tables si elles n'existent pas
        print("PostgreSQL initialisé avec URI :", app.config.get('SQLALCHEMY_DATABASE_URI'))
    except Exception as e:
        print("Erreur d'initialisation de PostgreSQL :", e)
