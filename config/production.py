import os
from .base import BaseConfig

class ProductionConfig(BaseConfig):
    DEBUG=False
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URL")
    REDIS_URI = os.getenv("REDIS_PRODUCTION")