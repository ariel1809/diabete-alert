# import os
# from dotenv import load_dotenv
#
# # Charger les variables d'environnement
# load_dotenv()
#
#
# class Config:
#     MONGO_USER = os.getenv("MONGO_USER", "arielo18")
#     MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "Azerty18")
#     MONGO_HOST = os.getenv("MONGO_HOST", "cluster0.ousup.mongodb.net")
#     MONGO_DB = os.getenv("MONGO_DB", "diabeteAlertDB")
#
#     # URI MongoDB corrigé pour MongoDB Atlas
#     MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}/{MONGO_DB}"

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "ariel")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "dpg-ctdj8gjgbbvc73fj39j0-a.oregon-postgres.render.com")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "dpg-ctdj8gjgbbvc73fj39j0-a")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "diabetedb")

    # URI PostgreSQL pour SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
