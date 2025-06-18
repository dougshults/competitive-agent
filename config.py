"""
Configuration settings for the Competitive Agent application.
"""

import os

class Config:
    """Base configuration."""
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or 'your-key-here'
    
    # Application Settings
    DEBUG = True
    PORT = 8080
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///competitive_agent.db'
    
    # AI Analysis settings
    MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'app.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = 10000000  # 10MB
    LOG_BACKUP_COUNT = 5

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'INFO'
    
    # Override with environment variables in production
    @classmethod
    def init_app(cls, app):
        """Initialize production-specific settings."""
        # Ensure required environment variables are set
        required_vars = ['OPENAI_API_KEY', 'SECRET_KEY']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'  # Use in-memory database for testing

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the appropriate configuration object."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default']) 