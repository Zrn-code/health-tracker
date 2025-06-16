from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any, Tuple
import logging

from services import user_service, health_service
from exceptions import HealthTrackerException, handle_exception
from logger import log_auth_attempt, log_registration_attempt, log_user_action

logger = logging.getLogger(__name__)

# Create blueprints
auth_bp = Blueprint('auth', __name__)
profile_bp = Blueprint('profile', __name__)
health_bp = Blueprint('health', __name__)

def create_response(data: Any = None, message: str = None, status_code: int = 200) -> Tuple[Dict[str, Any], int]:
    """Create standardized API response"""
    response = {}
    
    if message:
        response['message'] = message
    
    if data is not None:
        if isinstance(data, dict) and 'message' in data:
            response.update(data)
        else:
            response['data'] = data
    
    return response, status_code

def get_request_data():
    """Helper function to safely get request JSON data"""
    try:
        if not request.is_json:
            return None, "Content-Type must be application/json"
        
        data = request.get_json()
        if data is None:
            return None, "Invalid JSON data"
        
        return data, None
    except Exception as e:
        return None, f"Failed to parse JSON: {str(e)}"

# Authentication endpoints
@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data, error = get_request_data()
        if error:
            return create_response(message=error, status_code=400)
        
        result = user_service.register_user(data)
        
        log_registration_attempt(
            data.get('email', ''), 
            data.get('username', ''), 
            True
        )
        
        return create_response(result, status_code=201)
        
    except HealthTrackerException as e:
        log_registration_attempt(
            data.get('email', '') if 'data' in locals() and data else '',
            data.get('username', '') if 'data' in locals() and data else '',
            False,
            e.message
        )
        return create_response(message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return create_response(message="Internal server error", status_code=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data, error = get_request_data()
        if error:
            return create_response(message=error, status_code=400)
        
        username = data.get('username') or data.get('login')
        password = data.get('password')
        
        result = user_service.authenticate_user(username, password)
        
        log_auth_attempt(username, True)
        log_user_action(result['user_id'], 'LOGIN', f'User {username} logged in')
        
        return create_response(result)
        
    except HealthTrackerException as e:
        log_auth_attempt(username if 'username' in locals() else 'unknown', False, e.message)
        return create_response(message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Login error: {e}")
        return create_response(message="Internal server error", status_code=500)

# Profile endpoints
@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        logger.info(f"Getting profile for user: {user_id}")
        
        profile = user_service.get_user_profile(user_id)
        logger.info(f"Profile data retrieved: {profile}")
        
        return create_response(profile)
        
    except HealthTrackerException as e:
        logger.error(f"Profile service error: {e.message}")
        return create_response(message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Get profile error: {e}", exc_info=True)
        return create_response(message="Internal server error", status_code=500)

@profile_bp.route('/', methods=['POST'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        data, error = get_request_data()
        if error:
            return create_response(message=error, status_code=400)
        
        result = user_service.update_user_profile(user_id, data)
        
        log_user_action(user_id, 'PROFILE_UPDATED', 'User completed profile setup')
        
        return create_response(result)
        
    except HealthTrackerException as e:
        return create_response(message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return create_response(message="Internal server error", status_code=500)

@profile_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_account():
    """Delete user account"""
    try:
        user_id = get_jwt_identity()
        data, error = get_request_data()
        if error:
            return create_response(message=error, status_code=400)
        
        if not data.get('password'):
            return create_response(message="Password confirmation required", status_code=400)
        
        result = user_service.delete_user_account(user_id, data['password'])
        
        log_user_action(user_id, 'ACCOUNT_DELETED', 'User account and all data deleted')
        
        return create_response(result)
        
    except HealthTrackerException as e:
        return create_response(message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Delete account error: {e}")
        return create_response(message="Internal server error", status_code=500)

# Health endpoints
@health_bp.route('/daily-entry', methods=['POST'])
@jwt_required()
def submit_daily_data():
    """Submit daily health data"""
    try:
        user_id = get_jwt_identity()
        data, error = get_request_data()
        if error:
            return create_response(message=error, status_code=400)
        
        result = health_service.submit_daily_data(user_id, data)
        
        log_user_action(user_id, 'DAILY_ENTRY_CREATED', f'Created entry for {data.get("date")}')
        
        return create_response(result, status_code=201)
        
    except HealthTrackerException as e:
        return create_response(message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Submit daily data error: {e}")
        return create_response(message="Internal server error", status_code=500)

@health_bp.route('/daily-entries', methods=['GET'])
@jwt_required()
def get_daily_data():
    """Get user's daily data entries"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 30))
        
        result = health_service.get_daily_data(user_id, limit)
        
        return create_response(result)
        
    except HealthTrackerException as e:
        return create_response(message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Get daily data error: {e}")
        return create_response(message="Internal server error", status_code=500)

@health_bp.route('/suggestion', methods=['POST'])
@jwt_required()
def get_health_suggestion():
    """Get AI-powered health suggestion"""
    try:
        user_id = get_jwt_identity()
        
        result = health_service.generate_health_suggestion(user_id)
        
        log_user_action(user_id, 'HEALTH_SUGGESTION_GENERATED', 'Generated daily health suggestion')
        
        return create_response(result)
        
    except HealthTrackerException as e:
        return create_response(message=e.message, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Health suggestion error: {e}")
        return create_response(message="Internal server error", status_code=500)
