import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    MONGO_USER = os.getenv("MONGO_USER", "arielo18")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "Azerty18")
    MONGO_HOST = os.getenv("MONGO_HOST", "cluster0.ousup.mongodb.net")
    MONGO_DB = os.getenv("MONGO_DB", "diabeteAlertDB")

    # URI MongoDB corrigé pour MongoDB Atlas
    MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}/{MONGO_DB}"