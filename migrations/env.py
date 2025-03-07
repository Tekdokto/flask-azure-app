from flask import current_app
from flask_migrate import Migrate, upgrade
from app import database

migrate = Migrate()

def run_migrations():
    with current_app.app_context():
        upgrade()

if __name__ == "__main__":
    run_migrations()
