from flask import render_template, Blueprint

# Créer un blueprint pour les routes
web = Blueprint('route', __name__)

# Route pour la page du chatbot
@web.route('/login')
def login():
    return render_template('dashboard/authentication-login.html')

@web.route('/register')
def register():
    return render_template('dashboard/authentication-register.html')

@web.route('/index')
def index():
    return render_template('dashboard/index.html')
