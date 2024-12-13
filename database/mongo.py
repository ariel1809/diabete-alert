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
