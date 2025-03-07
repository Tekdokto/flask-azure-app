import os
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")
    FLASK_ENV = os.getenv("FLASK_ENV", "development").lower()

    if FLASK_ENV == "production":
        SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URL")
        REDIS_URI = os.getenv("REDIS_PRODUCTION")
    elif FLASK_ENV == "docker":
        SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL")
        REDIS_URI = os.getenv("REDIS_DOCKER")
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv("LOCAL_DATABASE_URL")
        REDIS_URI = os.getenv("REDIS_LOCAL")