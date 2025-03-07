import os
from dotenv import load_dotenv

load_dotenv()

from .development import DevelopmentConfig
from .production import ProductionConfig

FLASK_ENV = os.getenv("FLASK_ENV", "development").lower()
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if FLASK_ENV == "production" or ENVIRONMENT == "production":
    Config = ProductionConfig
elif FLASK_ENV == "docker" or ENVIRONMENT == "docker":
    Config = DevelopmentConfig
else:
    Config = DevelopmentConfig