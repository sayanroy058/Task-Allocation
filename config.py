import os
from db_config import get_db_connection_string

class Config:
    """Base config class"""
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'task_management_secret_key')
    SQLALCHEMY_DATABASE_URI = get_db_connection_string()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration for Gmail SMTP
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB max upload
    UPLOAD_FOLDER = 'uploads'

class DevelopmentConfig(Config):
    """Development config"""
    DEBUG = True

class ProductionConfig(Config):
    """Production config"""
    DEBUG = False
