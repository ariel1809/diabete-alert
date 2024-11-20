import os
from functools import wraps
import jwt
import datetime

from bson import ObjectId
from flask import render_template, Blueprint, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database.mongo import mongo

from models.model import User

# Créer un blueprint pour les routes
web = Blueprint('web', __name__)

# Clé secrète pour générer le JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'default_key_for_dev')

# Route pour la page de connexion
@web.route('/')
def accueil():
    return render_template("accueil.html")

@web.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        email = request.form.get('email')
        password = request.form.get('password')

        # Vérifier si l'email existe dans la base de données
        user = mongo.db.users.find_one({"email": email})

        # Si l'utilisateur existe et que le mot de passe est correct
        if user and check_password_hash(user['password'], password):
            # Générer un token JWT
            payload = {
                'user_id': str(user['_id']),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)  # Expiration du token (5 heures)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            # Ajouter le token dans la session
            session['token'] = token
            session['is_logged_in'] = True  # Ajouter un champ booléen pour savoir si l'utilisateur est connecté

            # Mettre à jour le statut de connexion dans la base de données
            mongo.db.users.update_one(
                {"_id": user['_id']},
                {"$set": {"is_logged_in": True}}  # Mettre à jour le champ 'is_logged_in' à True
            )

            return redirect(url_for('web.index'))  # Rediriger vers la page d'accueil

        # Si l'email ou le mot de passe est incorrect
        flash('Email ou mot de passe incorrect', 'danger')
        return render_template('authentication-login.html')  # Renvoyer le formulaire avec un message d'erreur

    return render_template('authentication-login.html')


# Route pour l'inscription
@web.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Récupérer toutes les données du formulaire
        form_data = request.form.to_dict()

        name = form_data.get('name')
        email = form_data.get('email')
        password = form_data.get('password')
        confirm_password = form_data.get('confirm_password')

        # Vérifier si les mots de passe correspondent
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('authentication-register.html', form_data=form_data)

        # Vérifier si l'utilisateur existe déjà
        if mongo.db.users.find_one({"email": email}):
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('authentication-register.html', form_data=form_data)

        # Ajouter l'utilisateur
        user = User(name, email, password)
        mongo.db.users.insert_one(user.to_dict())

        # Message de succès et redirection
        flash('Inscription réussie ! Connectez-vous pour continuer.', 'success')
        return redirect(url_for('web.login'))

    return render_template('authentication-register.html', form_data={})


# Fonction de vérification du token
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        # Récupérer le token de la session ou des en-têtes
        token = session.get('token')  # On suppose que le token est stocké dans la session

        if not token:
            flash('Vous devez être connecté pour accéder à cette page.', 'danger')
            return redirect(url_for('web.login'))  # Rediriger vers la page de connexion si pas de token

        try:
            # Décoder le token
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Récupérer l'ID de l'utilisateur à partir du token
            user_id = decoded_token['user_id']
        except jwt.ExpiredSignatureError:
            flash('Le token a expiré, veuillez vous reconnecter.', 'danger')
            return redirect(url_for('web.login'))
        except jwt.InvalidTokenError:
            flash('Token invalide, veuillez vous reconnecter.', 'danger')
            return redirect(url_for('web.login'))

        # Ajouter l'ID utilisateur à l'argument de la vue
        kwargs['user_id'] = user_id
        return f(*args, **kwargs)

    return decorator


# Route protégée pour la page d'accueil
@web.route('/index')
@token_required
def index(user_id):
    return render_template('index.html', user_id=user_id)

@web.route('/logout')
@token_required
def logout(user_id):
    # Convertir l'user_id en ObjectId si nécessaire
    try:
        user_id = ObjectId(user_id)  # Convertir le string en ObjectId
    except Exception as e:
        flash('ID de l\'utilisateur invalide.', 'danger')
        return redirect(url_for('web.login'))

    # Récupérer l'utilisateur à partir de la base de données
    user = mongo.db.users.find_one({"_id": user_id})

    if user:
        # Mettre à jour le statut de l'utilisateur dans la base de données
        mongo.db.users.update_one(
            {"_id": user_id},
            {"$set": {"is_logged_in": False}}  # Changer le statut 'is_logged_in' à False
        )

        # Vider la session
        session.pop('token', None)
        session.pop('is_logged_in', None)

        # Message de déconnexion
        flash('Vous êtes déconnecté avec succès.', 'success')
    else:
        flash('Utilisateur non trouvé.', 'danger')

    # Rediriger vers la page de connexion
    return redirect(url_for('web.login'))

