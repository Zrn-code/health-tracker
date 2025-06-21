# Health Tracker

A comprehensive health tracking application that helps users monitor their daily health metrics, receive AI-powered suggestions, and manage their wellness journey.

## Overview

Health Tracker is a full-stack web application designed to provide users with a complete health monitoring solution. The application combines modern web technologies with AI-powered insights to deliver personalized health recommendations.

### Key Features

- **User Management**: Secure registration, authentication, and profile management
- **Daily Health Tracking**: Record weight, height, meals, and other health metrics
- **AI-Powered Suggestions**: Personalized health recommendations using Google Gemini AI
- **Data Visualization**: Interactive charts and progress tracking
- **Secure Data Storage**: Firebase Firestore with comprehensive data validation
- **Real-time Updates**: Live data synchronization across devices
- **Responsive Design**: Optimized for desktop and mobile devices

## Project Structure

```markdown
health-tracker/
├── frontend/ # React + Vite frontend application
│ ├── src/
│ │ ├── components/ # Reusable UI components
│ │ ├── pages/ # Page components
│ │ ├── hooks/ # Custom React hooks
│ │ ├── services/ # API service layer
│ │ ├── utils/ # Utility functions
│ │ └── App.jsx # Main application component
│ └── package.json
├── backend/ # Python Flask + Firebase backend API
│ ├── api.py # API routes and endpoints
│ ├── app.py # Flask application main file
│ ├── services.py # Business logic service layer
│ ├── repositories.py # Data access layer
│ ├── validators.py # Input validation
│ ├── utils.py # AI services and utilities
│ ├── config.py # Application configuration
│ ├── Dockerfile # Docker configuration
│ └── requirements.txt # Python dependencies
└── README.md
```

## Quick Start

### Frontend Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at <http://localhost:5173>

### Backend Setup (Python Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend will run at <http://localhost:8080>

## Tech Stack

### Frontend

- **Framework**: React 18 + Vite
- **Routing**: React Router
- **HTTP Client**: Axios
- **Styling**: CSS Modules / Styled Components
- **Build Tool**: Vite

### Backend

- **Framework**: Flask + Flask-RESTX
- **Database**: Firebase Firestore
- **Authentication**: JWT (Flask-JWT-Extended)
- **AI Service**: Google Gemini AI
- **API Documentation**: Swagger (Flask-RESTX)
- **Deployment**: Docker + Google Cloud Run
- **CI/CD**: Automated testing and deployment pipeline

## Core Features

### 1. User Management

- **Registration & Login**: Secure user authentication with JWT tokens
- **Profile Management**: Personal information, health goals, and preferences
- **Account Security**: Password validation and secure data handling
- **Account Deletion**: Complete data removal with password confirmation

### 2. Health Data Tracking

- **Daily Entries**: Record weight, height, and meal information
- **Data Validation**: Comprehensive input validation and error handling
- **Historical Data**: View and manage past health records
- **Progress Tracking**: Monitor health trends over time

### 3. AI-Powered Health Suggestions

- **Personalized Recommendations**: AI-generated suggestions based on user data
- **Google Gemini AI**: Advanced AI model for health insights
- **Daily Limits**: One suggestion per day to maintain quality
- **Contextual Analysis**: Considers user profile and recent activity

### 4. Data Security & Privacy

- **JWT Authentication**: Secure token-based authentication
- **Data Encryption**: Sensitive information protection
- **Input Validation**: Comprehensive data validation
- **Audit Logging**: Complete activity tracking
- **Firebase Security**: Enterprise-grade database security

## API Endpoints

### Authentication

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### User Profile

- `GET /api/profile/` - Get user profile
- `POST /api/profile/` - Update user profile
- `DELETE /api/profile/delete` - Delete account

### Health Data

- `POST /api/health/daily-entry` - Create daily health record
- `GET /api/health/daily-entries` - Get health records
- `POST /api/health/suggestion` - Generate AI suggestions

### API Documentation

Access complete API documentation at `/api/docs/`

## Development

### Testing

The backend includes comprehensive testing with:

- Unit tests with pytest
- Integration tests for API endpoints
- Code coverage reporting
- Automated CI/CD pipeline

For detailed development instructions, see individual README files in the frontend and backend directories.
