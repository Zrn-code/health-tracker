from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any, Tuple
import logging
import json
from datetime import datetime

from services import user_service, health_service
from exceptions import HealthTrackerException, handle_exception
from logger import log_auth_attempt, log_registration_attempt, log_user_action

logger = logging.getLogger(__name__)

# Create namespaces
auth_ns = Namespace('auth', description='Authentication operations')
profile_ns = Namespace('profile', description='User profile operations')
health_ns = Namespace('health', description='Health data operations')

# Define models for request/response validation
auth_register_model = auth_ns.model('RegisterRequest', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password')
})

auth_login_model = auth_ns.model('LoginRequest', {
    'username': fields.String(required=True, description='Username or email'),
    'password': fields.String(required=True, description='Password')
})

profile_model = profile_ns.model('ProfileRequest', {
    'age': fields.Integer(description='User age'),
    'gender': fields.String(description='User gender'),
    'height': fields.Float(description='Height in cm'),
    'weight': fields.Float(description='Weight in kg'),
    'activity_level': fields.String(description='Activity level'),
    'health_goals': fields.List(fields.String, description='Health goals'),
    'birth_date': fields.String(description='Birth date in YYYY-MM-DD format'),
    'initial_height': fields.Float(description='Initial height in cm'),
    'initial_weight': fields.Float(description='Initial weight in kg')
})

daily_entry_model = health_ns.model('DailyEntryRequest', {
    'date': fields.String(required=True, description='Date in YYYY-MM-DD format'),
    'weight': fields.Float(description='Weight in kg'),
    'height': fields.Float(description='Height in cm'),
    'sleep_hours': fields.Float(description='Hours of sleep'),
    'water_intake': fields.Float(description='Water intake in liters'),
    'exercise_minutes': fields.Integer(description='Exercise minutes'),
    'mood': fields.String(description='Mood rating'),
    'notes': fields.String(description='Additional notes'),
    'breakfast': fields.String(description='Breakfast description'),
    'lunch': fields.String(description='Lunch description'),
    'dinner': fields.String(description='Dinner description')
})

delete_account_model = profile_ns.model('DeleteAccountRequest', {
    'password': fields.String(required=True, description='Password confirmation')
})

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

def serialize_response(data):
    """Serialize response data handling datetime objects"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if hasattr(value, 'isoformat'):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_response(value)
            elif isinstance(value, list):
                result[key] = [serialize_response(item) if isinstance(item, dict) else 
                             item.isoformat() if hasattr(item, 'isoformat') else item 
                             for item in value]
            else:
                result[key] = value
        return result
    return data

def get_request_data():
    """Helper function to safely get request JSON data"""
    try:
        # Check content type first
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            return None, "Content-Type must be application/json"
        
        # For Flask test client, check if we have JSON data
        if hasattr(request, 'is_json') and request.is_json:
            data = request.get_json()
            # Handle None case (empty JSON or parsing error)
            if data is None:
                return {}, None
            return data, None
        
        # Fallback: check if we have data but wrong content type
        if hasattr(request, 'data') and request.data:
            try:
                import json
                data = json.loads(request.data.decode('utf-8'))
                return data, None
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None, "Invalid JSON data"
        
        # No data at all but correct content type means empty JSON
        return {}, None
        
    except Exception as e:
        return None, f"Failed to parse JSON: {str(e)}"

# Authentication endpoints
@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(auth_register_model)
    @auth_ns.doc('register_user')
    def post(self):
        """Register a new user"""
        try:
            data, error = get_request_data()
            if error:
                return {'message': error}, 400
            
            result = user_service.register_user(data)
            
            log_registration_attempt(
                data.get('email', ''), 
                data.get('username', ''), 
                True
            )
            
            return serialize_response(result), 201
            
        except HealthTrackerException as e:
            log_registration_attempt(
                data.get('email', '') if 'data' in locals() and data else '',
                data.get('username', '') if 'data' in locals() and data else '',
                False,
                e.message
            )
            return {'message': e.message}, e.status_code
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {'message': 'Internal server error'}, 500

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(auth_login_model)
    @auth_ns.doc('login_user')
    def post(self):
        """Login user"""
        try:
            data, error = get_request_data()
            if error:
                return {'message': error}, 400
            
            username = data.get('username') or data.get('login')
            password = data.get('password')
            
            result = user_service.authenticate_user(username, password)
            
            log_auth_attempt(username, True)
            log_user_action(result['user_id'], 'LOGIN', f'User {username} logged in')
            
            return serialize_response(result)
            
        except HealthTrackerException as e:
            log_auth_attempt(username if 'username' in locals() else 'unknown', False, e.message)
            return {'message': e.message}, e.status_code
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'message': 'Internal server error'}, 500

# Profile endpoints
@profile_ns.route('/')
class Profile(Resource):
    @jwt_required()
    @profile_ns.doc('get_profile', security='Bearer')
    def get(self):
        """Get user profile"""
        try:
            user_id = get_jwt_identity()
            logger.info(f"Getting profile for user: {user_id}")
            
            profile = user_service.get_user_profile(user_id)
            logger.info(f"Profile data retrieved: {profile}")
            
            return serialize_response(profile)
            
        except HealthTrackerException as e:
            logger.error(f"Profile service error: {e.message}")
            return {'message': e.message}, e.status_code
        except Exception as e:
            logger.error(f"Get profile error: {e}", exc_info=True)
            return {'message': 'Internal server error'}, 500

    @jwt_required()
    @profile_ns.expect(profile_model)
    @profile_ns.doc('update_profile', security='Bearer')
    def post(self):
        """Update user profile"""
        try:
            user_id = get_jwt_identity()
            data, error = get_request_data()
            if error:
                return {'message': error}, 400
            
            result = user_service.update_user_profile(user_id, data)
            
            log_user_action(user_id, 'PROFILE_UPDATED', 'User completed profile setup')
            
            return serialize_response(result)
            
        except HealthTrackerException as e:
            return {'message': e.message}, e.status_code
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            return {'message': 'Internal server error'}, 500

@profile_ns.route('/delete')
class DeleteAccount(Resource):
    @jwt_required()
    @profile_ns.expect(delete_account_model)
    @profile_ns.doc('delete_account', security='Bearer')
    def delete(self):
        """Delete user account"""
        try:
            user_id = get_jwt_identity()
            data, error = get_request_data()
            if error:
                return {'message': error}, 400
            
            if not data.get('password'):
                return {'message': 'Password confirmation required'}, 400
            
            result = user_service.delete_user_account(user_id, data['password'])
            
            log_user_action(user_id, 'ACCOUNT_DELETED', 'User account and all data deleted')
            
            return serialize_response(result)
            
        except HealthTrackerException as e:
            return {'message': e.message}, e.status_code
        except Exception as e:
            logger.error(f"Delete account error: {e}")
            return {'message': 'Internal server error'}, 500

# Health endpoints
@health_ns.route('/daily-entry')
class DailyEntry(Resource):
    @jwt_required()
    @health_ns.expect(daily_entry_model)
    @health_ns.doc('submit_daily_data', security='Bearer')
    def post(self):
        """Submit daily health data"""
        try:
            user_id = get_jwt_identity()
            data, error = get_request_data()
            if error:
                return {'message': error}, 400
            
            result = health_service.submit_daily_data(user_id, data)
            
            log_user_action(user_id, 'DAILY_ENTRY_CREATED', f'Created entry for {data.get("date")}')
            
            return serialize_response(result), 201
            
        except HealthTrackerException as e:
            return {'message': e.message}, e.status_code
        except Exception as e:
            logger.error(f"Submit daily data error: {e}")
            return {'message': 'Internal server error'}, 500

@health_ns.route('/daily-entries')
class DailyEntries(Resource):
    @jwt_required()
    @health_ns.doc('get_daily_data', security='Bearer')
    @health_ns.param('limit', 'Number of entries to retrieve', type=int, default=30)
    def get(self):
        """Get user's daily data entries"""
        try:
            user_id = get_jwt_identity()
            limit = int(request.args.get('limit', 30))
            
            result = health_service.get_daily_data(user_id, limit)
            
            return serialize_response(result)
            
        except HealthTrackerException as e:
            return {'message': e.message}, e.status_code
        except Exception as e:
            logger.error(f"Get daily data error: {e}")
            return {'message': 'Internal server error'}, 500

@health_ns.route('/suggestion')
class HealthSuggestion(Resource):
    @jwt_required()
    @health_ns.doc('get_health_suggestion', security='Bearer')
    def post(self):
        """Get AI-powered health suggestion"""
        try:
            user_id = get_jwt_identity()
            
            result = health_service.generate_health_suggestion(user_id)
            
            log_user_action(user_id, 'HEALTH_SUGGESTION_GENERATED', 'Generated daily health suggestion')
            
            return serialize_response(result)
            
        except HealthTrackerException as e:
            return {'message': e.message}, e.status_code
        except Exception as e:
            logger.error(f"Health suggestion error: {e}")
            return {'message': 'Internal server error'}, 500
