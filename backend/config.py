import os
from datetime import timedelta
from typing import List, Optional

class Config:
    """Application configuration"""
    
    # Security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'xxx')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:5173',  # Vite dev server
        'http://localhost:3000',  # React dev server
        'https://interview-c8310.web.app',
        'https://interview-c8310.firebaseapp.com'
    ]
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', "X-Requested-With"]
    CORS_EXPOSE_HEADERS = ['Content-Type', 'Authorization']
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', './secret/firebase')
    
    # Gemini AI settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Server settings
    PORT = int(os.environ.get('PORT', 8080))
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # Database settings
    MAX_DAILY_ENTRIES = 30
    MAX_SUGGESTION_PER_DAY = 1
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DIR = os.environ.get('LOG_DIR', 'logs')
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of missing required settings"""
        errors = []
        
        if not os.path.exists(cls.FIREBASE_CREDENTIALS_PATH):
            errors.append(f"Firebase credentials file not found: {cls.FIREBASE_CREDENTIALS_PATH}")
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY environment variable not set")
        
        return errors

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    JWT_SECRET_KEY = 'test-secret-key'
    FIREBASE_CREDENTIALS_PATH = 'test-firebase-creds.json'

# Configuration factory
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration object by name"""
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    return config_by_name.get(config_name, DevelopmentConfig)
