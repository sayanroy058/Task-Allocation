import os
import logging

# Load environment variables from .env file
from load_env import load_env
load_env()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from utils import mail
from db_config import get_db_connection_string

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set up database base class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the Flask app
app = Flask(__name__)
# Ensure a secure secret key is set
if os.environ.get("SESSION_SECRET"):
    app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET")
else:
    app.config["SECRET_KEY"] = "task_management_secret_key_for_development"
app.secret_key = app.config["SECRET_KEY"]  # Ensure both are set for compatibility
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = get_db_connection_string()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure file uploads
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1GB max upload
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")

# Make sure upload folder exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Configure email
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "krishnajayanth418@gmail.com"
app.config["MAIL_PASSWORD"] = "msvx epik apwc dmpr"
app.config["MAIL_DEFAULT_SENDER"] = "krishnajayanth418@gmail.com"
app.config["ADMIN_EMAILS"] = ["krishnajayanth418@gmail.com"]  # Admin emails for notifications

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"
mail.init_app(app)

# Import routes after app is created to avoid circular imports
from routes import register_routes
register_routes(app)

# Initialize database
with app.app_context():
    import models  # noqa: F401
    try:
        db.create_all()
        logging.info("Database tables created successfully")
        
        # Create admin user if not exists
        from routes import create_admin
        create_admin()
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")