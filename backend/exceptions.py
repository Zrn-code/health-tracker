from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class HealthTrackerException(Exception):
    """Base exception for Health Tracker application"""
    
    def __init__(self, message: str, status_code: int = 500, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        result = {'error': self.message}
        if self.payload:
            result.update(self.payload)
        return result

class ValidationError(HealthTrackerException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, 400, {'field': field} if field else None)

class AuthenticationError(HealthTrackerException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)

class AuthorizationError(HealthTrackerException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, 403)

class NotFoundError(HealthTrackerException):
    """Raised when resource is not found"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)

class ConflictError(HealthTrackerException):
    """Raised when resource conflict occurs"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, 409)

class ServiceUnavailableError(HealthTrackerException):
    """Service unavailable error"""
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, 503)

class DatabaseError(HealthTrackerException):
    """Raised when database operations fail"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, 500)
        logger.error(f"Database error: {message}")

def handle_exception(e: Exception) -> Dict[str, Any]:
    """Generic exception handler"""
    if isinstance(e, HealthTrackerException):
        return e.to_dict(), e.status_code
    
    # Log unexpected errors
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    return {'error': 'Internal server error'}, 500
