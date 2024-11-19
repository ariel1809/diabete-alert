from flask import Flask, request, jsonify, render_template


# Créer une instance de l'application Flask
app = Flask(__name__)

# Route pour la page du chatbot
@app.route('/login')
def login():
    return render_template('dashboard/authentication-login.html')

@app.route('/register')
def register():
    return render_template('dashboard/authentication-register.html')

@app.route('/index')
def index():
    return render_template('dashboard/index.html')