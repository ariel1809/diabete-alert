from werkzeug.security import generate_password_hash
from datetime import datetime

class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)  # Hachage du mot de passe
        self.created_at = datetime.utcnow()
        self.is_logged_in = False

    def to_dict(self):
        """
        Convertir l'objet User en dictionnaire pour MongoDB.
        """
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            'is_logged_in': self.is_logged_in
        }