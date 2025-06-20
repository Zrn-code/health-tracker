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

# Define response models for documentation - 修正為實際返回的格式
auth_response_model = auth_ns.model('AuthResponse', {
    'access_token': fields.String(description='JWT access token'),
    'user_id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email address')
})

error_model = auth_ns.model('ErrorResponse', {
    'message': fields.String(description='Error message')
})

# Profile 響應模型需要與實際返回的數據匹配
profile_response_model = profile_ns.model('ProfileResponse', {
    'user_id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email address'),
    'age': fields.Integer(description='User age', allow_null=True),
    'gender': fields.String(description='User gender', allow_null=True),
    'height': fields.Float(description='Height in cm', allow_null=True),
    'weight': fields.Float(description='Weight in kg', allow_null=True),
    'activity_level': fields.String(description='Activity level', allow_null=True),
    'health_goals': fields.List(fields.String, description='Health goals', allow_null=True),
    'birth_date': fields.String(description='Birth date', allow_null=True),
    'initial_height': fields.Float(description='Initial height in cm', allow_null=True),
    'initial_weight': fields.Float(description='Initial weight in kg', allow_null=True),
    'created_at': fields.String(description='Account creation date'),
    'updated_at': fields.String(description='Last profile update date', allow_null=True)
})

# Daily entry 響應模型
daily_entry_response_model = health_ns.model('DailyEntryResponse', {
    'id': fields.Integer(description='Entry ID'),
    'user_id': fields.Integer(description='User ID'),
    'date': fields.String(description='Entry date'),
    'weight': fields.Float(description='Weight in kg', allow_null=True),
    'height': fields.Float(description='Height in cm', allow_null=True),
    'sleep_hours': fields.Float(description='Hours of sleep', allow_null=True),
    'water_intake': fields.Float(description='Water intake in liters', allow_null=True),
    'exercise_minutes': fields.Integer(description='Exercise minutes', allow_null=True),
    'mood': fields.String(description='Mood rating', allow_null=True),
    'notes': fields.String(description='Additional notes', allow_null=True),
    'breakfast': fields.String(description='Breakfast description', allow_null=True),
    'lunch': fields.String(description='Lunch description', allow_null=True),
    'dinner': fields.String(description='Dinner description', allow_null=True),
    'created_at': fields.String(description='Entry creation timestamp'),
    'updated_at': fields.String(description='Entry last update timestamp', allow_null=True)
})

# Daily entries 列表響應模型
daily_entries_response_model = health_ns.model('DailyEntriesResponse', {
    'entries': fields.List(fields.Nested(daily_entry_response_model), description='List of daily entries'),
    'total_count': fields.Integer(description='Total number of entries'),
    'limit': fields.Integer(description='Limit used for pagination')
})

# Health suggestion 響應模型
health_suggestion_response_model = health_ns.model('HealthSuggestionResponse', {
    'suggestion': fields.String(description='AI-generated health suggestion'),
    'generated_at': fields.String(description='Suggestion generation timestamp'),
    'user_id': fields.Integer(description='User ID')
})

# 統一的成功消息模型
success_message_model = profile_ns.model('SuccessMessage', {
    'message': fields.String(description='Success message')
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
    @auth_ns.expect(auth_register_model, validate=True)
    @auth_ns.doc('register_user',
                 description='Register a new user account with username, email, and password',
                 responses={
                     201: ('User registered successfully', auth_response_model),
                     400: ('Bad request - invalid input data', error_model),
                     409: ('Conflict - username or email already exists', error_model),
                     500: ('Internal server error', error_model)
                 })
    def post(self):
        """
        Register a new user
        
        Creates a new user account with the provided credentials.
        Username and email must be unique across the system.
        Password must meet security requirements (minimum 8 characters).
        
        Returns JWT access token upon successful registration.
        """
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
    @auth_ns.expect(auth_login_model, validate=True)
    @auth_ns.doc('login_user',
                 description='Authenticate user with username/email and password',
                 responses={
                     200: ('Login successful', auth_response_model),
                     400: ('Bad request - missing credentials', error_model),
                     401: ('Unauthorized - invalid credentials', error_model),
                     500: ('Internal server error', error_model)
                 })
    def post(self):
        """
        User login
        
        Authenticates user with username or email and password.
        Returns JWT access token for authenticated requests.
        Token expires after configured time period.
        """
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
    @profile_ns.doc('get_profile',
                    description='Retrieve current user profile information',
                    security='Bearer',
                    responses={
                        200: ('Profile retrieved successfully', profile_response_model),
                        401: ('Unauthorized - invalid or missing token', error_model),
                        404: ('User not found', error_model),
                        500: ('Internal server error', error_model)
                    })
    def get(self):
        """
        Get user profile
        
        Retrieves complete profile information for the authenticated user.
        Includes personal details, health metrics, and preferences.
        """
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
    @profile_ns.expect(profile_model, validate=True)
    @profile_ns.doc('update_profile',
                    description='Update user profile with new information',
                    security='Bearer',
                    responses={
                        200: ('Profile updated successfully', profile_response_model),
                        400: ('Bad request - invalid profile data', error_model),
                        401: ('Unauthorized - invalid or missing token', error_model),
                        422: ('Validation error - invalid field values', error_model),
                        500: ('Internal server error', error_model)
                    })
    def post(self):
        """
        Update user profile
        
        Updates user profile information including:
        - Personal details (age, gender, birth_date)
        - Physical metrics (height, weight, initial measurements)
        - Health preferences (activity_level, health_goals)
        
        All fields are optional - only provided fields will be updated.
        """
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
    @profile_ns.expect(delete_account_model, validate=True)
    @profile_ns.doc('delete_account',
                    description='Permanently delete user account and all associated data',
                    security='Bearer',
                    responses={
                        200: ('Account deleted successfully', success_message_model),
                        400: ('Bad request - password confirmation required', error_model),
                        401: ('Unauthorized - invalid or missing token', error_model),
                        403: ('Forbidden - incorrect password', error_model),
                        500: ('Internal server error', error_model)
                    })
    def delete(self):
        """
        Delete user account
        
        Permanently deletes the user account and all associated data including:
        - User profile information
        - All daily health entries
        - Account preferences and settings
        
        This action cannot be undone. Password confirmation is required.
        """
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
    @health_ns.expect(daily_entry_model, validate=True)
    @health_ns.doc('submit_daily_data',
                   description='Submit daily health tracking data',
                   security='Bearer',
                   responses={
                       201: ('Daily entry created successfully', daily_entry_response_model),
                       400: ('Bad request - invalid data format', error_model),
                       401: ('Unauthorized - invalid or missing token', error_model),
                       409: ('Conflict - entry already exists for this date', error_model),
                       422: ('Validation error - invalid field values', error_model),
                       500: ('Internal server error', error_model)
                   })
    def post(self):
        """
        Submit daily health data
        
        Creates a new daily health entry with tracked metrics:
        - Physical measurements (weight, height)
        - Lifestyle data (sleep_hours, water_intake, exercise_minutes)
        - Wellness tracking (mood, notes)
        - Meal information (breakfast, lunch, dinner)
        
        Date must be in YYYY-MM-DD format. Only one entry per date is allowed.
        """
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
    @health_ns.doc('get_daily_data',
                   description='Retrieve user daily health entries with pagination',
                   security='Bearer',
                   params={
                       'limit': {
                           'description': 'Maximum number of entries to return (1-100)',
                           'type': 'integer',
                           'default': 30,
                           'minimum': 1,
                           'maximum': 100
                       }
                   },
                   responses={
                       200: ('Daily entries retrieved successfully', daily_entries_response_model),
                       400: ('Bad request - invalid limit parameter', error_model),
                       401: ('Unauthorized - invalid or missing token', error_model),
                       500: ('Internal server error', error_model)
                   })
    def get(self):
        """
        Get daily health entries
        
        Retrieves paginated list of user's daily health entries.
        Entries are returned in reverse chronological order (most recent first).
        
        Use limit parameter to control number of entries returned (max 100).
        """
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
    @health_ns.doc('get_health_suggestion',
                   description='Generate AI-powered personalized health suggestion',
                   security='Bearer',
                   responses={
                       200: ('Health suggestion generated successfully', health_suggestion_response_model),
                       401: ('Unauthorized - invalid or missing token', error_model),
                       404: ('User profile incomplete - cannot generate suggestion', error_model),
                       429: ('Too many requests - rate limit exceeded', error_model),
                       500: ('Internal server error', error_model),
                       503: ('Service unavailable - AI service temporarily down', error_model)
                   })
    def post(self):
        """
        Generate health suggestion
        
        Creates personalized AI-powered health recommendations based on:
        - User profile information (age, gender, health goals)
        - Recent daily health entries and trends
        - Activity patterns and lifestyle data
        
        Suggestions may include recommendations for:
        - Exercise routines and activity levels
        - Nutrition and meal planning
        - Sleep optimization
        - Wellness and mental health tips
        
        Requires complete user profile and recent daily entries for best results.
        """
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
            return {'message': e.message}, e.status_code
        except Exception as e:
            logger.error(f"Health suggestion error: {e}")
            return {'message': 'Internal server error'}, 500
