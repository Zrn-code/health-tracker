from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api
import logging
import os

from config import get_config
from exceptions import HealthTrackerException, handle_exception
from logger import health_logger
from api import auth_ns, profile_ns, health_ns

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Validate configuration
    config_errors = config.validate()
    if config_errors:
        for error in config_errors:
            print(f"Configuration error: {error}")
    
    # Initialize CORS with more explicit configuration
    CORS(app,resources=
        {r"/api/*": {"origins": config.CORS_ORIGINS},r"/api/docs":{"origins": "*"}},
        supports_credentials=config.CORS_SUPPORTS_CREDENTIALS,
        methods=config.CORS_METHODS,
        max_age=3600,
        allow_headers=config.CORS_ALLOW_HEADERS,
        expose_headers=config.CORS_EXPOSE_HEADERS
    )
    
    jwt = JWTManager(app)
    
    # Initialize Flask-RESTX
    api = Api(
        app,
        version='2.0.0',
        title='Health Tracker API',
        description='''
        A comprehensive health tracking API with user management and daily health data tracking.
        
        ## Authentication
        Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:
        ```
        Authorization: Bearer <your-jwt-token>
        ```
        
        ## API Features
        - User registration and authentication
        - Comprehensive user profile management
        - Daily health data tracking
        - AI-powered health suggestions
        - Secure data handling with input validation
        
        ## Data Formats
        - All dates should be in YYYY-MM-DD format
        - Timestamps are returned in ISO 8601 format
        - All requests should use Content-Type: application/json
        ''',
        doc='/api/docs/',
        prefix='/api',
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Add "Bearer " before your JWT token. Example: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            }
        },
        security='Bearer',
        validate=True,
        ordered=True
    )
    
    # Initialize logging
    health_logger.init_app(app)

    # Register namespaces
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(profile_ns, path='/profile')
    api.add_namespace(health_ns, path='/health')
    
    # Error handlers
    register_error_handlers(app)
    
    return app


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(HealthTrackerException)
    def handle_health_tracker_exception(e):
        return jsonify(e.to_dict()), e.status_code
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        response, status_code = handle_exception(e)
        return jsonify(response), status_code

# Create app instance
app = create_app()

if __name__ == '__main__':
    config = get_config()
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG
    )
