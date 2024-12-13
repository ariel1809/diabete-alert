import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "ariel")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "DqZrN28aRqkpzQqbOJiB8zWXaYuodXbr")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "dpg-ctdj8gjgbbvc73fj39j0-a.oregon-postgres.render.com")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "diabetedb")

    # URI PostgreSQL pour SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
