# local imports
from . import main
from app.models import Users
from .. import db, limiter

# library/packages imports
from flask import render_template, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

#systems import
import base64
from datetime import datetime, timedelta

SECRET_KEY = "ryyf79fnn99fneejjjje99jrj3nneii"

""" This routes receives user data as a json and stores it  database. No headers required"""
@main.route("/register", methods= ["POST","GET"])
def register():
    """Submit a json with user  to this route"""
    data = request.get_json()

    if not isinstance(data, dict):
        return make_response(jsonify({"error": "Payload must be a JSON object"}), 400)
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    phone_number = data.get('phone_number', '').strip()
    id_number = data.get('id_number', '').strip()
    password = data.get('password', '').strip()

    if not phone_number or not password:
        return make_response(jsonify({"error": "All fields are required"}), 400)

    if len(password) < 8:
        return make_response(jsonify({"error": "Password must be at least 8 characters"}), 400)

    if Users.query.filter_by(phone_number=phone_number).first():
        return make_response(jsonify({"error": "The user is already registered"}), 409)

    hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

    new_user = Users(
        first_name= first_name,
        last_name = last_name,
        phone_number = phone_number,
        id_number = id_number,
        password = hashed_pw
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({"message": "User registered successfully"}), 201)
    except Exception as e:
        return make_response(jsonify({"error": "Server error", "details": str(e)}), 500)

""" After a user has registered, now login and in this route they are issued a jwt token.
No  body. Sent phone number and password as basic authorization header """
@main.route("/login", methods= ["POST"])
def login():

    #get the phone number and password from the header that they submit
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Basic "):
        return make_response(jsonify({"error": "Missing or invalid Authorization header"}), 401)

    try:
        # Decode the base64 string
        base64_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(base64_credentials).decode("utf-8")

        # Split into phone number and password
        user_name, password = decoded_credentials.split(":", 1)

        # Fetch user from DB
        user = Users.query.filter_by(phone_number=user_name).first()
        if not user :
            return make_response(jsonify({"error": "The user is not registered"}), 401)
        if not check_password_hash(user.password, password):
            return make_response(jsonify({"error": "Wrong password provided"}), 401)

        # Generate JWT
        payload = {
            "sub": str(user.id),
            "phone_number": user.phone_number,
            "exp": datetime.utcnow() + timedelta(hours=1)
            }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"token": token})
    except Exception as e:
        return make_response(jsonify({"error": "Login failed", "details": str(e)}), 500)