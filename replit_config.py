"""
Replit Configuration Helper
This module provides configuration utilities for running the PropTech Intel app on Replit.
"""

import os
import logging
from pathlib import Path

def verify_project_structure():
    """Verify that the required project files exist."""
    required_files = [
        'requirements.txt',  # Should exist in your GitHub repo
    ]
    
    optional_files = [
        'app.py',
        'static/',
        'templates/',
        'models.py',
        'routes.py',
    ]
    
    missing_required = []
    missing_optional = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_required.append(file_path)
    
    for file_path in optional_files:
        if not Path(file_path).exists():
            missing_optional.append(file_path)
    
    if missing_required:
        logging.error(f"Missing required files: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        logging.warning(f"Missing optional files: {', '.join(missing_optional)}")
    
    return True

def setup_environment_variables():
    """Set up environment variables with fallbacks for development."""
    
    env_vars = {
        'FLASK_APP': 'main.py',
        'FLASK_ENV': 'production',
        'FLASK_DEBUG': '1',
        'PYTHONUNBUFFERED': '1',
    }
    
    for key, value in env_vars.items():
        if not os.environ.get(key):
            os.environ[key] = value
            logging.info(f"Set {key} = {value}")

def get_secret_with_fallback(secret_name, fallback=None):
    """Get a secret from environment variables with fallback."""
    value = os.environ.get(secret_name, fallback)
    if not value and not fallback:
        logging.warning(f"Secret {secret_name} not found in environment variables")
    return value

def configure_flask_app(app):
    """Configure Flask app for Replit deployment."""
    
    # Basic Flask configuration
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-change-me')
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = True
    
    # Static and template folders
    app.static_folder = 'static'
    app.template_folder = 'templates'
    
    # Database configuration (if using SQLAlchemy)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_recycle': 300,
            'pool_pre_ping': True,
        }
    
    # API configurations
    app.config['OPENAI_API_KEY'] = get_secret_with_fallback('OPENAI_API_KEY')
    
    logging.info("Flask app configured for Replit deployment")
    return app

if __name__ == '__main__':
    # Run verification
    if verify_project_structure():
        logging.info("Project structure verification passed")
    else:
        logging.error("Project structure verification failed")
