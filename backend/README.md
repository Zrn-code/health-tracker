# Health Tracker Backend

Python Flask + Firebase Backend API Service

## Requirements

- Python 3.10+
- pip
- Firebase Firestore
- Google Gemini AI API Key

## Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Configure the following variables in your system environment

# Start development server
python app.py

# Or start with Gunicorn
gunicorn -b :8080 app:app
```

## API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### User Profile (`/api/profile`)

- `GET /api/profile/` - Get user profile
- `POST /api/profile/` - Update user profile
- `DELETE /api/profile/delete` - Delete user account

### Health Data (`/api/health`)

- `POST /api/health/daily-entry` - Create daily health record
- `GET /api/health/daily-entries` - Get health records list
- `POST /api/health/suggestion` - Generate AI health suggestions

### API Documentation

Visit `/api/docs/` to view complete Swagger API documentation

## Project Structure

```text
backend/
├── api.py              # API routes and endpoint definitions
├── app.py              # Flask application main file
├── config.py           # Application configuration
├── services.py         # Business logic service layer
├── repositories.py     # Data access layer
├── validators.py       # Input data validation
├── utils.py            # AI services and utility functions
├── exceptions.py       # Custom exception handling
├── logger.py           # Logging configuration
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container configuration
├── hello.json          # Firebase service account key
├── pytest.ini          # Test configuration
└── logs/               # Log files directory
```

## Tech Stack

- **Framework**: Flask + Flask-RESTX
- **Database**: Firebase Firestore
- **Authentication**: JWT (Flask-JWT-Extended)
- **AI Service**: Google Gemini AI
- **API Documentation**: Swagger (Flask-RESTX)
- **Logging**: Python logging with rotation
- **Deployment**: Docker + Google Cloud Run
- **CI/CD**: Automated testing and deployment pipeline

## Core Features

1. **User Management**

   - Registration and login authentication
   - Personal profile management
   - Account deletion

2. **Health Data Tracking**

   - Daily health records
   - Physical metrics tracking
   - Meal logging

3. **AI Health Suggestions**

   - Personalized recommendations based on user data
   - Powered by Google Gemini AI
   - Daily limit of one suggestion

4. **Data Security**
   - JWT token authentication
   - Input data validation
   - Sensitive data encryption
   - Comprehensive logging

## CI/CD Continuous Integration

### Testing Framework

- **Unit Testing**: pytest
- **Test Coverage**: pytest-cov
- **API Testing**: Flask test client
- **Test Configuration**: pytest.ini

### Test Commands

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=. --cov-report=html

# Run specific test markers
pytest -m unit              # Unit tests
pytest -m integration       # Integration tests
pytest -m api               # API endpoint tests
pytest -m "not slow"        # Exclude slow tests
```

### Automation Pipeline

- **GitHub Actions**: Automated CI/CD pipeline
- **Automated Testing**: Triggered on every commit
- **Code Quality Check**: Automatic code standard validation
- **Automated Deployment**: Auto-deploy to Cloud Run after tests pass
- **Containerization**: Automated Docker build and push

### Deployment Environments

- **Development**: Local development and testing
- **Production**: Google Cloud Run
- **Monitoring**: Application logs and performance monitoring
