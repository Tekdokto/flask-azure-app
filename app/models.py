from . import database
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Candidate(database.Model):
    __tablename__ = "candidates"

    id = database.Column(database.Integer, primary_key=True)
    full_name = database.Column(database.String(150), nullable=False)
    username = database.Column(database.String(100), unique=True, nullable=False)
    email = database.Column(database.String(100), unique=True, nullable=False)
    password_hash = database.Column(database.String(256), nullable=False)
    profession = database.Column(database.String(100), nullable=False)
    country = database.Column(database.String(100), nullable=False)
    state = database.Column(database.String(100), nullable=False)
    city = database.Column(database.String(100), nullable=False)
    gender = database.Column(database.String(20), nullable=False)
    marital_status = database.Column(database.String(100), nullable=False)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def set_password(self, password):
        """Hash and store candidate's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify candidate's password"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert candidate object to dictionary for JSON responses"""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "email": self.email,
            "profession": self.profession,
            "gender": self.gender,
            "country": self.country,
            "state": self.state,
            "city": self.city,
            "marital_status": self.marital_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Candidate {self.username}, Email: {self.email}, CreatedAt: {self.created_at}>"






