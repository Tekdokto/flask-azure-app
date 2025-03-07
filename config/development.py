import os
from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL")
    REDIS_URI = os.getenv("REDIS_LOCAL")