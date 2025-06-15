import os
from datetime import timedelta

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:5173',  # Vite dev server
        'http://localhost:3000',  # React dev server
        'https://your-firebase-app.web.app',  # Firebase hosting
        'https://your-firebase-app.firebaseapp.com'  # Firebase hosting alternative
    ]
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH = 'hello.json'
    
    # Gemini AI settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Server settings
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
