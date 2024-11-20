import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = os.getenv("MONGO_PORT", 27017)
    MONGO_DB = os.getenv("MONGO_DB", "diabeteAlertDB")
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"