import os
import jwt
import datetime
import joblib
import pandas as pd
from flask import render_template, Blueprint, request, jsonify, redirect, url_for, flash, session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash
from models.model import User, db, Prediction  # Importer le modèle User et db
from functools import wraps
from scipy.special import expit

# Clé secrète pour générer le JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'default_key_for_dev')

# Charger le modèle ML
model = joblib.load("diabetes.pkl")

# Créer un blueprint pour les routes
web = Blueprint('web', __name__)

# Route pour la page de connexion
@web.route('/')
def accueil():
    return render_template("accueil.html")

@web.route('/data')
def data():
    return render_template("data.html")

@web.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Vérifier si l'utilisateur existe dans la base de données PostgreSQL
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Générer un token JWT
            payload = {
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            # Ajouter le token dans la session
            session['token'] = token
            session['is_logged_in'] = True  # Ajouter un champ booléen pour savoir si l'utilisateur est connecté

            # Mettre à jour le statut de connexion dans la base de données
            user.is_logged_in = True
            db.session.commit()

            return redirect(url_for('web.index'))  # Rediriger vers la page d'accueil

        flash('Email ou mot de passe incorrect', 'danger')
        return render_template('authentication-login.html')

    return render_template('authentication-login.html')

# Route pour l'inscription
@web.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        name = form_data.get('name')
        email = form_data.get('email')
        password = form_data.get('password')
        confirm_password = form_data.get('confirm_password')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('authentication-register.html', form_data=form_data)

        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('authentication-register.html', form_data=form_data)

        # Ajouter l'utilisateur
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash('Inscription réussie ! Connectez-vous pour continuer.', 'success')
        return redirect(url_for('web.login'))

    return render_template('authentication-register.html', form_data={})

# Fonction de vérification du token
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = session.get('token')

        if not token:
            flash('Vous devez être connecté pour accéder à cette page.', 'danger')
            return redirect(url_for('web.login'))

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']
        except jwt.ExpiredSignatureError:
            flash('Le token a expiré, veuillez vous reconnecter.', 'danger')
            return redirect(url_for('web.login'))
        except jwt.InvalidTokenError:
            flash('Token invalide, veuillez vous reconnecter.', 'danger')
            return redirect(url_for('web.login'))

        kwargs['user_id'] = user_id
        return f(*args, **kwargs)

    return decorator

# Route protégée pour la page d'accueil
@web.route('/index')
@token_required
def index(user_id):
    # Récupérer toutes les données des patients depuis la base de données
    patients = Prediction.query.all()

    # Préparer les données pour le tableau
    patient_data = [
        {
            "id": patient.id,
            "pregnancies": patient.pregnancies,
            "glucose": patient.glucose,
            "blood_pressure": patient.blood_pressure,
            "skin_thickness": patient.skin_thickness,
            "insulin": patient.insulin,
            "bmi": patient.bmi,
            "pedigree": patient.pedigree,
            "age": patient.age,
            "is_diabetic": "Yes" if patient.is_diabetic else "No"
        }
        for patient in patients
    ]

    # Récupérer les statistiques
    diabetic_count = db.session.query(Prediction).filter_by(is_diabetic=True).count()
    non_diabetic_count = db.session.query(Prediction).filter_by(is_diabetic=False).count()

    return render_template('index.html', user_id=user_id, diabetic_count=diabetic_count, non_diabetic_count=non_diabetic_count, patient_data=patient_data)

@web.route('/logout')
@token_required
def logout(user_id):
    user = User.query.get(user_id)

    if user:
        user.is_logged_in = False
        db.session.commit()

        session.pop('token', None)
        session.pop('is_logged_in', None)

        flash('Vous êtes déconnecté avec succès.', 'success')
    else:
        flash('Utilisateur non trouvé.', 'danger')

    return redirect(url_for('web.login'))

# Route pour la prédiction
@web.route('/prediction')
@token_required
def prediction(user_id):
    return render_template('prediction.html')

def save_prediction_to_db(user_data, result):
    """
    Enregistre les données de la prédiction dans la base de données.
    """
    try:
        prediction = Prediction(
            pregnancies=user_data['Pregnancies'][0],
            glucose=user_data['Glucose'][0],
            blood_pressure=user_data['BloodPressure'][0],
            skin_thickness=user_data['SkinThickness'][0],
            insulin=user_data['Insulin'][0],
            bmi=user_data['BMI'][0],
            pedigree=user_data['DiabetesPedigreeFunction'][0],
            age=user_data['Age'][0],
            is_diabetic=(result == "Diabetic")
        )
        db.session.add(prediction)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

@web.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        required_fields = ['pregnancies', 'glucose', 'bloodPressure', 'skinThickness', 'insulin', 'bmi', 'pedigree', 'age']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing JSON fields'}), 400

        user_data = {
            'Pregnancies': [int(data['pregnancies'])],
            'Glucose': [float(data['glucose'])],
            'BloodPressure': [float(data['bloodPressure'])],
            'SkinThickness': [float(data['skinThickness'])],
            'Insulin': [float(data['insulin'])],
            'BMI': [float(data['bmi'])],
            'DiabetesPedigreeFunction': [float(data['pedigree'])],
            'Age': [int(data['age'])]
        }

        user_df = pd.DataFrame(user_data)

        # Obtenir les scores de décision
        decision_scores = model.decision_function(user_df)

        # Transformer en pseudo-probabilités
        prob_diabetic = expit(decision_scores[0])  # Probabilité d'être Diabetic
        prob_non_diabetic = 1 - prob_diabetic      # Probabilité d'être Non-Diabetic

        # Résultat basé sur le score
        result = "Diabetic" if prob_diabetic > 0.5 else "Non-Diabetic"

        # Enregistrer dans la base de données
        save_prediction_to_db(user_data, result)

        return jsonify({
            'result': result,
            'probability_diabetic': f"{prob_diabetic * 100:.2f}%",
            'probability_non_diabetic': f"{prob_non_diabetic * 100:.2f}%"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@web.route("/stats", methods=["POST"])
def get_stats():
    try:
        # Compter les patients diabétiques et non diabétiques
        diabetic_count = db.session.query(User).filter_by(is_diabetic=True).count()
        non_diabetic_count = db.session.query(User).filter_by(is_diabetic=False).count()

        return jsonify({
            "diabetic_count": diabetic_count,
            "non_diabetic_count": non_diabetic_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#route pour afficher le diagramme
@web.route('/stats/chart')
@token_required
def stats_chart():
    try:
        # Récupérer les statistiques depuis la base de données
        diabetic_count = db.session.query(Prediction).filter_by(is_diabetic=True).count()
        non_diabetic_count = db.session.query(Prediction).filter_by(is_diabetic=False).count()

        # Passer les données à la page HTML
        return render_template(
            'index.html',
            diabetic_count=diabetic_count,
            non_diabetic_count=non_diabetic_count
        )
    except Exception as e:
        flash('Erreur lors de la récupération des statistiques', 'danger')
        return redirect(url_for('web.index'))