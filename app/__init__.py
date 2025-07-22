# app/__init__.py
import os
from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Base class for model_class
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

""" The rate limiter function tries to convert the html error message to a json"""

limiter = Limiter(
    key_func=get_remote_address
)

def create_app():
    app = Flask(__name__, instance_relative_config=True) # Enable instance folder
    limiter.init_app(app)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists

    # Define DB path relative to instance folder for better portability
    db_path = os.path.join(app.instance_path, "cafes.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # Optional: Disable modification tracking

    db.init_app(app)

    # Register blueprints
    # Import blueprints *after* db is initialized but before create_all
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Create tables within the application context
    with app.app_context():
        # Import models *inside* the context and after db is initialized
        # This avoids potential circular imports if models need the app context
        db.create_all()


    return app
