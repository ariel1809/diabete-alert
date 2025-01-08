import os
from flask import Flask
from dashboar import web
from config import Config
from database import init_db, db
from flask_migrate import Migrate

app = Flask(__name__)
# Charger la configuration
app.config.from_object(Config)

# Initialiser la connexion MongoDB
init_db(app)

# Initialiser Flask-Migrate
migrate = Migrate(app, db)

# Enregistrer le blueprint des routes
app.register_blueprint(web)
app.secret_key = os.getenv('SECRET_KEY', 'default_key_for_dev')

if __name__ == '__main__':
    app.run(debug=True)