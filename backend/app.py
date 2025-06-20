from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
import os

from config import get_config
from exceptions import HealthTrackerException, handle_exception
from logger import health_logger
from api import auth_bp, profile_bp, health_bp

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
        {r"*": {"origins": '*'}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        expose_headers=["Content-Type", "Authorization"]
    )
    
    jwt = JWTManager(app)
    
    # Initialize logging
    health_logger.init_app(app)

    # Register blueprints with API prefix
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    
    # Error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'timestamp': '2024-01-01T00:00:00Z'
        })
    
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
