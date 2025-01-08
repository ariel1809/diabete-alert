from database.mongo import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_logged_in = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(100), nullable=True, default='dashboard/images/profile/user-1.jpg')

    def __init__(self, name, email, password, is_logged_in=False, profile_image='dashboard/images/profile/user-1.jpg'):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.is_logged_in = is_logged_in
        self.profile_image = profile_image

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'profile_image': self.profile_image,
            'is_logged_in': self.is_logged_in
        }


class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    pregnancies = db.Column(db.Integer, nullable=False)
    glucose = db.Column(db.Float, nullable=False)
    blood_pressure = db.Column(db.Float, nullable=False)
    skin_thickness = db.Column(db.Float, nullable=False)
    insulin = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    pedigree = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    is_diabetic = db.Column(db.Boolean, nullable=False)