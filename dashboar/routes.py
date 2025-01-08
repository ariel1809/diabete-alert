import os
import jwt
import datetime
import joblib
import pandas as pd
from flask import render_template, Blueprint, request, jsonify, redirect, url_for, flash, session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from models.model import User, db, Prediction  # Importer le modèle User et db
from functools import wraps
from scipy.special import expit
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Charger les variables d'environnement
load_dotenv()

# Clé secrète pour générer le JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'default_key_for_dev')

# Récupérer les configurations
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_EMAILS = os.getenv('TO_EMAILS').split(',')


# Charger le modèle ML
model = joblib.load("diabetes.pkl")

# Créer un blueprint pour les routes
web = Blueprint('web', __name__)

# Route pour la page de connexion
@web.route('/')
def accueil():
    return render_template("accueil.html")

@web.route('/send_mail', methods=['POST'])
def send_mail():
    try:
        # Récupération des données du formulaire
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        date = request.form.get('date')
        message = request.form.get('message')

        # Création de l'email
        msg = MIMEMultipart()
        msg['From'] = email  # L'email de l'utilisateur
        msg['To'] = ', '.join(TO_EMAILS)
        msg['Subject'] = f'Nouveau message de {name}'

        body = f"""
        Nom: {name}
        Email: {email}
        Téléphone: {phone if phone else 'Non renseigné'}
        Date: {date if date else 'Non renseignée'}
        Message: {message}
        """
        msg.attach(MIMEText(body, 'plain'))

        # Envoi de l'email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(email, TO_EMAILS, msg.as_string())

        flash('Votre message a été envoyé avec succès.', 'success')
        return redirect(url_for('web.accueil'))

    except Exception as e:
        flash(f'Erreur lors de l\'envoi du message : {str(e)}', 'danger')
        return redirect(url_for('web.accueil'))


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

        # Vérification de la correspondance des mots de passe
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('authentication-register.html', form_data=form_data)

        # Vérification si l'email est déjà utilisé
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('authentication-register.html', form_data=form_data)

        # Ajouter l'utilisateur avec une photo de profil par défaut
        default_profile_image = 'dashboard/images/profile/user-1.jpg'
        user = User(name=name, email=email, password=password, profile_image=default_profile_image)
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
    # Récupérer l'utilisateur en fonction de l'ID
    user = User.query.get(user_id)

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

    return render_template(
        'index.html',
        user=user,  # Passer l'objet 'user' au template
        diabetic_count=diabetic_count,
        non_diabetic_count=non_diabetic_count,
        patient_data=patient_data
    )
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
@token_required
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


# Route pour afficher et modifier le profil de l'utilisateur
@web.route('/profile', methods=['GET', 'POST'])
@token_required
def profile(user_id):
    user = User.query.get(user_id)

    # Vérification si l'utilisateur a une image de profil, sinon on assigne une image par défaut
    if not user.profile_image:
        user.profile_image = 'dashboard/images/profile/user-1.jpg'

    if request.method == 'POST':
        # Récupérer les données du formulaire pour modifier le profil
        name = request.form.get('name')
        email = request.form.get('email')
        image = request.files.get('image')

        # Vérifier si l'image a été téléchargée
        if image:
            image_path = os.path.join('static', 'profile_images', image.filename)
            image.save(image_path)
            user.profile_image = image_path

        # Mettre à jour les informations de l'utilisateur
        if name:
            user.name = name
        if email:
            user.email = email

        db.session.commit()
        flash('Votre profil a été mis à jour avec succès.', 'success')
        return redirect(url_for('web.profile'))

    return render_template('profile.html', user=user)

# Route pour changer le mot de passe
@web.route('/change_password', methods=['POST'])
@token_required
def change_password(user_id):
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    user = User.query.get(user_id)

    if not check_password_hash(user.password, current_password):
        flash("Le mot de passe actuel est incorrect", "danger")
        return redirect(url_for('web.profile'))

    if new_password != confirm_password:
        flash("Les mots de passe ne correspondent pas", "danger")
        return redirect(url_for('web.profile'))

    # Mise à jour du mot de passe
    user.password = generate_password_hash(new_password)
    db.session.commit()

    flash("Mot de passe modifié avec succès", "success")
    return redirect(url_for('web.profile'))

# Route pour changer la photo de profil
@web.route('/change_profile_picture', methods=['POST'])
@token_required
def change_profile_picture(user_id):
    user = User.query.get(user_id)
    file = request.files.get('profile_picture')

    if file:
        filename = secure_filename(file.filename)

        # Vérifier si le répertoire existe, sinon le créer
        profile_pictures_dir = 'static/dashboard/images/profile'
        dir = 'dashboard/images/profile'
        if not os.path.exists(profile_pictures_dir):
            os.makedirs(profile_pictures_dir)

        # Si un fichier de profil existe déjà, supprimer l'ancienne image
        if user.profile_image:
            old_picture_path = os.path.join(profile_pictures_dir, user.profile_image)
            if os.path.exists(old_picture_path):
                os.remove(old_picture_path)

        # Sauvegarder le fichier téléchargé dans le répertoire
        file.save(os.path.join(profile_pictures_dir, filename))

        # Mise à jour du chemin de la photo de profil dans la base de données
        user.profile_image = dir + "/"+ filename
        db.session.commit()

        flash("Photo de profil modifiée avec succès", "success")
    else:
        flash("Veuillez télécharger un fichier", "danger")

    return redirect(url_for('web.profile'))