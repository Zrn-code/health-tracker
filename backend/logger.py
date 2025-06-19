import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
from datetime import datetime
from flask import request, g
import json
import platform

class HealthTrackerLogger:
    """Centralized logging service for Health Tracker application"""
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger('health_tracker')
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize logging for Flask app"""
        self.app = app
        self.setup_file_logging()
        self.setup_console_logging()
        self.setup_request_logging()
        self.setup_jwt_logging()
        self.logger.info("Health Tracker logging system initialized")
    
    def setup_file_logging(self):
        """Setup file-based logging with rotation"""
        # Create logs directory if it doesn't exist
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Use different rotation strategy for Cloud Run
        is_cloud_run = os.getenv('K_SERVICE') is not None
        is_windows = platform.system() == 'Windows'
        
        if is_cloud_run or is_windows:
            # For Cloud Run and Windows, use simpler file handling to avoid permission issues
            main_handler = logging.FileHandler(
                os.path.join(log_dir, 'health-tracker.log'),
                mode='a',
                encoding='utf-8'
            )
            
            error_handler = logging.FileHandler(
                os.path.join(log_dir, 'error.log'),
                mode='a',
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            
            security_handler = logging.FileHandler(
                os.path.join(log_dir, 'security.log'),
                mode='a',
                encoding='utf-8'
            )
        else:
            # For Unix-like systems, use rotation
            main_handler = RotatingFileHandler(
                os.path.join(log_dir, 'health-tracker.log'),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=10
            )
            
            error_handler = TimedRotatingFileHandler(
                os.path.join(log_dir, 'error.log'),
                when='midnight',
                interval=1,
                backupCount=30
            )
            error_handler.setLevel(logging.ERROR)
            
            security_handler = RotatingFileHandler(
                os.path.join(log_dir, 'security.log'),
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=5
            )
        
        # Set formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] - %(message)s'
        )
        
        main_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        security_handler.setFormatter(simple_formatter)
        
        # Add handlers to loggers
        self.logger.addHandler(main_handler)
        self.logger.addHandler(error_handler)
        
        # Create security logger
        self.security_logger = logging.getLogger('security')
        self.security_logger.addHandler(security_handler)
        self.security_logger.setLevel(logging.INFO)
        
        # Set logging level based on environment
        if self.app and self.app.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
    
    def setup_console_logging(self):
        """Setup console logging for development and Cloud Run"""
        # Always enable console logging for Cloud Run
        is_cloud_run = os.getenv('K_SERVICE') is not None
        if (self.app and self.app.debug) or is_cloud_run:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def setup_request_logging(self):
        """Setup request/response logging middleware"""
        @self.app.before_request
        def log_request_info():
            g.start_time = datetime.utcnow()
            
            # Log basic request info
            try:
                self.logger.info(
                    f'Request: {request.method} {request.url} - '
                    f'IP: {request.remote_addr} - '
                    f'User-Agent: {request.headers.get("User-Agent", "Unknown")}'
                )
                
                # Log request data for POST/PUT requests (excluding sensitive data)
                if request.method in ['POST', 'PUT'] and request.is_json:
                    try:
                        data = request.get_json()
                        safe_data = self._sanitize_request_data(data)
                        if safe_data:
                            self.logger.debug(f'Request data: {json.dumps(safe_data, default=str)}')
                    except Exception as e:
                        self.logger.warning(f'Failed to log request data: {e}')
            except Exception as e:
                # Don't let logging errors break the request
                pass
        
        @self.app.after_request
        def log_response_info(response):
            try:
                if hasattr(g, 'start_time'):
                    duration = datetime.utcnow() - g.start_time
                    
                    # Determine log level based on status code
                    if response.status_code >= 500:
                        log_level = logging.ERROR
                    elif response.status_code >= 400:
                        log_level = logging.WARNING
                    else:
                        log_level = logging.INFO
                    
                    self.logger.log(
                        log_level,
                        f'Response: {response.status_code} - '
                        f'Duration: {duration.total_seconds():.3f}s - '
                        f'Size: {response.content_length or 0} bytes'
                    )
            except Exception as e:
                # Don't let logging errors break the response
                pass
            
            return response
    
    def setup_jwt_logging(self):
        """Setup JWT-specific logging"""
        def log_jwt_event(event_type, message):
            try:
                self.security_logger.warning(
                    f'JWT {event_type}: {message} - IP: {request.remote_addr} - '
                    f'Time: {datetime.utcnow().isoformat()}'
                )
            except Exception:
                # Don't let logging errors break the application
                pass
        
        # Store reference for use in JWT error handlers
        self.log_jwt_event = log_jwt_event
    
    def _sanitize_request_data(self, data):
        """Remove sensitive information from request data for logging"""
        if not isinstance(data, dict):
            return data
        
        sensitive_fields = {
            'password', 'token', 'access_token', 'refresh_token',
            'secret', 'key', 'credential', 'auth'
        }
        
        sanitized = {}
        for key, value in data.items():
            if key.lower() in sensitive_fields:
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_request_data(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def log_user_action(self, user_id, action, details=None):
        """Log user-specific actions"""
        try:
            message = f'User {user_id} - {action}'
            if details:
                message += f' - {details}'
            
            self.logger.info(message)
        except Exception:
            # Don't let logging errors break the application
            pass
    
    def log_security_event(self, event_type, details, user_id=None):
        """Log security-related events"""
        try:
            message = f'Security Event: {event_type}'
            if user_id:
                message += f' - User: {user_id}'
            if details:
                message += f' - {details}'
            
            self.security_logger.warning(message)
        except Exception:
            # Don't let logging errors break the application
            pass
    
    def log_auth_attempt(self, username, success, reason=None):
        """Log authentication attempts"""
        try:
            status = 'SUCCESS' if success else 'FAILED'
            message = f'Auth {status}: {username} - IP: {request.remote_addr}'
            if reason and not success:
                message += f' - Reason: {reason}'
            
            if success:
                self.security_logger.info(message)
            else:
                self.security_logger.warning(message)
        except Exception:
            # Don't let logging errors break the application
            pass
    
    def log_registration_attempt(self, email, username, success, reason=None):
        """Log registration attempts"""
        try:
            status = 'SUCCESS' if success else 'FAILED'
            message = f'Registration {status}: {username} ({email}) - IP: {request.remote_addr}'
            if reason and not success:
                message += f' - Reason: {reason}'
            
            if success:
                self.security_logger.info(message)
            else:
                self.security_logger.warning(message)
        except Exception:
            # Don't let logging errors break the application
            pass
    
    def get_logger(self, name=None):
        """Get a logger instance"""
        if name:
            return logging.getLogger(f'health_tracker.{name}')
        return self.logger

# Global logger instance
health_logger = HealthTrackerLogger()

# Convenience functions for easy import
def get_logger(name=None):
    """Get a logger instance"""
    return health_logger.get_logger(name)

def log_user_action(user_id, action, details=None):
    """Log user-specific actions"""
    health_logger.log_user_action(user_id, action, details)

def log_security_event(event_type, details, user_id=None):
    """Log security-related events"""
    health_logger.log_security_event(event_type, details, user_id)

def log_auth_attempt(username, success, reason=None):
    """Log authentication attempts"""
    health_logger.log_auth_attempt(username, success, reason)

def log_registration_attempt(email, username, success, reason=None):
    """Log registration attempts"""
    health_logger.log_registration_attempt(email, username, success, reason)
