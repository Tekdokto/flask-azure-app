from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Candidate
from . import database, cache, limiter, redis_client
from .utils import logger
import datetime

bp = Blueprint("main", __name__)

@bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.json
    logger.info(f"Received registration request for username: {data['username']}")

    if Candidate.query.filter_by(username=data['username']).first():
        logger.warning(f"Username {data['username']} already exists")
        return jsonify({'Error': 'username already exists!'}), 400
    if Candidate.query.filter_by(email=data['email']).first():
        logger.warning(f"Email {data['email']} already registered")
        return jsonify({'Error': 'email already exists!'}), 400

    new_candidate = Candidate(
        full_name=data['full_name'],
        username=data['username'],
        email=data['email'],
        profession=data['profession'],
        country=data['country'],
        state=data['state'],
        city=data['city'],
        gender=data['gender'],
        marital_status=data['marital_status']
    )

    new_candidate.set_password(data['password'])

    # Save to the database
    try:
        database.session.add(new_candidate)
        database.session.commit()
        logger.info(f"User {data['username']} registered successfully")
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        logger.error(f"Database error during registration: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.json
    logger.info(f"Login attempt for username: {data['username']}")

    candidate = Candidate.query.filter_by(username=data['username']).first()

    if candidate and candidate.check_password(data['password']):
        access_token = create_access_token(identity=candidate.id, expires_delta=datetime.timedelta(days=1))
        logger.info(f"User {data['username']} logged in successfully")
        return jsonify(candidate=candidate.to_dict(), access_token=access_token), 200

    logger.warning(f"Failed login attempt for username: {data['username']}")
    return jsonify({'Error': 'Invalid credentials!'}), 401

@bp.route("/candidates", methods=["GET"])
@cache.cached(timeout=60)
def get_candidates():
    """Retrieve all candidates and return as JSON."""
    candidates = Candidate.query.all()
    return jsonify([candidate.to_dict() for candidate in candidates])  # ✅ Convert objects to dictionaries

@bp.route("/candidate/<int:id>", methods=["GET"])
def get_candidate(id):
    cache_key = f"candidate_{id}"
    cached_candidate = redis_client.get(cache_key)

    if cached_candidate:
        logger.info("From redis")
        jsonify(eval(cached_candidate)) # String back to dictionary

    candidate = Candidate.query.get(id)
    if not candidate:
        jsonify({'Error': 'Candidate not found!'})

    candidate_dict = candidate.to_dict()
    redis_client.setex(cache_key, 300, str(candidate_dict))
    return jsonify(candidate_dict)

@bp.route("/candidate/<int:id>", methods=["PUT"])
def update_candidate(id):
    """Update an existing candidate's information."""
    candidate = Candidate.query.get(id)

    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    data = request.json  # Get JSON request data

    # ✅ Update fields only if they exist in the request
    candidate.full_name = data.get("full_name", candidate.full_name)
    candidate.username = data.get("username", candidate.username)
    candidate.email = data.get("email", candidate.email)
    candidate.profession = data.get("profession", candidate.profession)
    candidate.country = data.get("country", candidate.country)
    candidate.state = data.get("state", candidate.state)
    candidate.city = data.get("city", candidate.city)
    candidate.gender = data.get("gender", candidate.gender)
    candidate.marital_status = data.get("marital_status", candidate.marital_status)

    try:
        db.session.commit()
        cache_key = f"candidate_{id}"
        redis_client.setex(cache_key, 300, str(candidate.to_dict()))  # ✅ Update Redis cache
        return jsonify({"message": "Candidate updated successfully", "candidate": candidate.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@bp.route("/candidate/<int:id>", methods=["DELETE"])
def delete_candidate(id):
    """Delete a candidate from the database and remove from cache."""
    candidate = Candidate.query.get(id)

    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    try:
        db.session.delete(candidate)
        db.session.commit()
        cache_key = f"candidate_{id}"
        redis_client.delete(cache_key)  # ✅ Remove from Redis cache
        return jsonify({"message": "Candidate deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
