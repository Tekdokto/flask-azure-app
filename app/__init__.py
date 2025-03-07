from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config.settings import Config
from dotenv import load_dotenv
import os
import redis
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


load_dotenv()

database = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

REDIS_URL = Config.REDIS_URI
# Initialize redis
redis_client = redis.Redis.from_url(
    REDIS_URL, decode_responses=True
)
# Setup caching
cache = Cache(
    config={
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": REDIS_URL
    }
)
# Setup rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL,
    strategy="fixed-window"
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    database.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, database)
    cache.init_app(app)
    limiter.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        database.create_all()

    return app