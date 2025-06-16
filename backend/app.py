from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restx import Api, Resource, fields, Namespace
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import firebase_admin
from firebase_admin import credentials, firestore
from google import genai
import os
import numpy as np
import logging
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app, 
     origins=Config.CORS_ORIGINS,
     methods=Config.CORS_METHODS,
     allow_headers=Config.CORS_ALLOW_HEADERS,
     supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS)
jwt = JWTManager(app)

# Initialize Flask-RESTX
api = Api(
    app,
    version='1.0',
    title='Health Tracker API',
    description='A comprehensive health tracking system with daily data recording and AI-powered health suggestions',
    doc='/docs/',  # Swagger UI will be available at /docs/
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Add "Bearer " before your token'
        }
    },
    security='Bearer'
)

# Create namespaces
auth_ns = Namespace('auth', description='Authentication operations')
profile_ns = Namespace('profile', description='User profile operations')
health_ns = Namespace('health', description='Health data and suggestions')
api.add_namespace(auth_ns, path='/api/auth')
api.add_namespace(profile_ns, path='/api/profile')
api.add_namespace(health_ns, path='/api/health')

# Define models for documentation
user_register_model = api.model('UserRegister', {
    'email': fields.String(required=True, description='User email address', example='user@example.com'),
    'username': fields.String(required=True, description='Unique username', example='healthuser123'),
    'password': fields.String(required=True, description='User password (min 6 characters)', example='securepass123')
})

user_login_model = api.model('UserLogin', {
    'username': fields.String(required=True, description='Username or email', example='healthuser123'),
    'password': fields.String(required=True, description='User password', example='securepass123')
})

profile_model = api.model('UserProfile', {
    'birth_date': fields.String(required=True, description='Birth date (YYYY-MM-DD)', example='1990-05-15'),
    'initial_height': fields.Float(required=True, description='Initial height in cm', example=175.0),
    'initial_weight': fields.Float(required=True, description='Initial weight in kg', example=70.5)
})

daily_data_model = api.model('DailyData', {
    'date': fields.String(required=True, description='Date (YYYY-MM-DD)', example='2024-01-15'),
    'height': fields.Float(required=True, description='Height in cm', example=175.0),
    'weight': fields.Float(required=True, description='Weight in kg', example=70.5),
    'breakfast': fields.String(required=True, description='Breakfast description', example='Oatmeal with fruits'),
    'lunch': fields.String(required=True, description='Lunch description', example='Grilled chicken salad'),
    'dinner': fields.String(required=True, description='Dinner description', example='Steamed fish with vegetables')
})

delete_account_model = api.model('DeleteAccount', {
    'password': fields.String(required=True, description='Current password for confirmation', example='securepass123')
})

# Response models
success_response = api.model('SuccessResponse', {
    'message': fields.String(description='Success message'),
    'data': fields.Raw(description='Response data')
})

error_response = api.model('ErrorResponse', {
    'error': fields.String(description='Error message')
})

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase initialization error: {e}")

db = firestore.client()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize Gemini AI
api_key = Config.GEMINI_API_KEY
if api_key:
    genai_client = genai.Client(api_key=api_key)
else:
    genai_client = None
    logger.warning("GEMINI_API_KEY not found - health suggestions will be disabled")



# Authentication endpoints
@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_register_model, validate=True)
    @auth_ns.marshal_with(success_response, code=201)
    @auth_ns.response(400, 'Missing required fields or invalid data', error_response)
    @auth_ns.response(409, 'User already exists', error_response)
    def post(self):
        """Register a new user"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['email', 'username', 'password']
            if not all(field in data for field in required_fields):
                return {'error': 'Missing required fields'}, 400
            
            # Validate email contains @
            if '@' not in data['email']:
                return {'error': 'Invalid email format'}, 400
            
            # Validate username doesn't contain @
            if '@' in data['username']:
                return {'error': 'Username cannot contain @ symbol'}, 400
            
            # Check if user already exists using modern filter syntax
            users_ref = db.collection('users')
            existing_user = users_ref.where(filter=firestore.FieldFilter('email', '==', data['email'])).get()
            
            if existing_user:
                return {'error': 'User already exists'}, 409
            
            # Check if username already exists
            existing_username = users_ref.where(filter=firestore.FieldFilter('username', '==', data['username'])).get()
            if existing_username:
                return {'error': 'Username already exists'}, 409
            
            # Create new user
            hashed_password = generate_password_hash(data['password'])
            user_data = {
                'email': data['email'],
                'username': data['username'],
                'password': hashed_password,
                'created_at': datetime.now(timezone.utc),
                'profile_completed': False
            }
            
            doc_ref = users_ref.add(user_data)
            user_id = doc_ref[1].id
            
            return {
                'message': 'User registered successfully',
                'user_id': user_id
            }, 201
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {'error': 'Internal server error'}, 500

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_login_model, validate=True)
    @auth_ns.marshal_with(success_response, code=200)
    @auth_ns.response(400, 'Missing credentials', error_response)
    @auth_ns.response(401, 'Invalid credentials', error_response)
    def post(self):
        """Login user - supports both username and email"""
        try:
            data = request.get_json()
            
            # Accept either 'username' or 'login' field for backward compatibility
            login_identifier = data.get('username') or data.get('login')
            password = data.get('password')
            
            if not login_identifier or not password:
                return {'error': 'Username/email and password required'}, 400
            
            # Find user by username or email using modern filter syntax
            users_ref = db.collection('users')
            user_docs = None
            
            # Check if login identifier contains @ (likely email)
            if '@' in login_identifier:
                # Search by email
                user_docs = users_ref.where(filter=firestore.FieldFilter('email', '==', login_identifier)).get()
            else:
                # Search by username
                user_docs = users_ref.where(filter=firestore.FieldFilter('username', '==', login_identifier)).get()
            
            if not user_docs:
                return {'error': 'Invalid credentials'}, 401
            
            user_doc = user_docs[0]
            user_data = user_doc.to_dict()
            
            # Verify password
            if not check_password_hash(user_data['password'], password):
                return {'error': 'Invalid credentials'}, 401
            
            # Generate JWT token
            access_token = create_access_token(identity=user_doc.id)
            
            return {
                'message': 'Login successful',
                'access_token': access_token,
                'user_id': user_doc.id,
                'profile_completed': user_data.get('profile_completed', False)
            }, 200
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'error': 'Internal server error'}, 500

# Profile endpoints
@profile_ns.route('/')
class Profile(Resource):
    @jwt_required()
    @auth_ns.marshal_with(success_response, code=200)
    @auth_ns.response(401, 'Authentication required', error_response)
    @auth_ns.response(404, 'User not found', error_response)
    def get(self):
        """Get user profile"""
        try:
            user_id = get_jwt_identity()
            user_doc = db.collection('users').document(user_id).get()
            
            if not user_doc.exists:
                return {'error': 'User not found'}, 404
            
            user_data = user_doc.to_dict()
            
            # Remove sensitive information
            user_data.pop('password', None)
            
            return user_data, 200
            
        except Exception as e:
            logger.error(f"Get profile error: {e}")
            return {'error': 'Internal server error'}, 500
    
    @jwt_required()
    @profile_ns.expect(profile_model, validate=True)
    @profile_ns.marshal_with(success_response, code=200)
    @profile_ns.response(400, 'Missing required fields', error_response)
    @profile_ns.response(401, 'Authentication required', error_response)
    def post(self):
        """Submit user profile"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['birth_date', 'initial_height', 'initial_weight']
            if not all(field in data for field in required_fields):
                return {'error': 'Missing required fields'}, 400
            
            # Update user profile
            profile_data = {
                'birth_date': datetime.strptime(data['birth_date'], '%Y-%m-%d'),
                'initial_height': float(data['initial_height']),
                'initial_weight': float(data['initial_weight']),
                'profile_completed': True,
                'updated_at': datetime.now(timezone.utc)
            }
            
            db.collection('users').document(user_id).update(profile_data)
            
            return {
                'message': 'Profile submitted successfully'
            }, 200
            
        except Exception as e:
            logger.error(f"Profile submission error: {e}")
            return {'error': 'Internal server error'}, 500

@profile_ns.route('/delete-account')
class DeleteAccount(Resource):
    @jwt_required()
    @profile_ns.expect(delete_account_model, validate=True)
    @profile_ns.marshal_with(success_response, code=200)
    @profile_ns.response(400, 'Password confirmation required', error_response)
    @profile_ns.response(401, 'Invalid password or authentication required', error_response)
    @profile_ns.response(404, 'User not found', error_response)
    def delete(self):
        """Delete user account and all associated data"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # Require password confirmation
            if not data or not data.get('password'):
                return {'error': 'Password confirmation required'}, 400
            
            # Get user document to verify existence and password
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return {'error': 'User not found'}, 404
            
            user_data = user_doc.to_dict()
            
            # Verify password
            if not check_password_hash(user_data['password'], data['password']):
                logger.warning(f"Account deletion failed - invalid password for user: {user_id}")
                return {'error': 'Invalid password'}, 401
            
            # Delete user's daily entries
            daily_entries = db.collection('daily_entries').where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).get()
            
            for entry in daily_entries:
                entry.reference.delete()
            
            # Delete user's health suggestions
            health_suggestions = db.collection('health_suggestions').where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).get()
            
            for suggestion in health_suggestions:
                suggestion.reference.delete()
            
            # Delete user document
            db.collection('users').document(user_id).delete()
            
            logger.info(f"Account deleted successfully for user: {user_id}")
            
            return {
                'message': 'Account and all associated data deleted successfully'
            }, 200
            
        except Exception as e:
            logger.error(f"Account deletion error: {e}")
            return {'error': 'Internal server error'}, 500

# Health endpoints
@health_ns.route('/daily-entry')
class DailyEntry(Resource):
    @jwt_required()
    @health_ns.expect(daily_data_model, validate=True)
    @health_ns.marshal_with(success_response, code=201)
    @health_ns.response(400, 'Missing required fields', error_response)
    @health_ns.response(401, 'Authentication required', error_response)
    @health_ns.response(409, 'Entry already exists for this date', error_response)
    def post(self):
        """Submit daily health data"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['date', 'height', 'weight', 'breakfast', 'lunch', 'dinner']
            if not all(field in data for field in required_fields):
                return {'error': 'Missing required fields'}, 400
            
            # Parse date and convert to datetime for Firestore compatibility
            entry_date = datetime.strptime(data['date'], '%Y-%m-%d')
            entry_date_only = entry_date.date()  # Keep date object for comparison
            
            # Check if entry already exists for this date using modern filter syntax
            existing_entry = db.collection('daily_entries').where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).where(
                filter=firestore.FieldFilter('date', '==', entry_date)
            ).get()
            
            if existing_entry:
                return {'error': 'Entry already exists for this date'}, 409
            
            # Create daily entry - use datetime object for Firestore
            entry_data = {
                'user_id': user_id,
                'date': entry_date,  # Store as datetime object
                'height': float(data['height']),
                'weight': float(data['weight']),
                'breakfast': data['breakfast'],
                'lunch': data['lunch'],
                'dinner': data['dinner'],
                'created_at': datetime.now(timezone.utc)
            }
            
            doc_ref = db.collection('daily_entries').add(entry_data)
            
            return {
                'message': 'Daily data submitted successfully',
                'entry_id': doc_ref[1].id
            }, 201
            
        except Exception as e:
            logger.error(f"Daily data submission error: {e}")
            return {'error': 'Internal server error'}, 500

@health_ns.route('/daily-entries')
class DailyEntries(Resource):
    @jwt_required()
    @health_ns.marshal_with(success_response, code=200)
    @health_ns.response(401, 'Authentication required', error_response)
    @health_ns.param('limit', 'Maximum number of entries to return', type=int, default=30)
    def get(self):
        """Get user's daily health data entries"""
        try:
            user_id = get_jwt_identity()
            
            # Get query parameters
            limit = int(request.args.get('limit', 30))
            
            # Fetch entries using modern filter syntax
            entries_ref = db.collection('daily_entries').where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).order_by('date', direction=firestore.Query.DESCENDING).limit(limit)
            entries = entries_ref.get()
            
            entries_data = []
            for entry in entries:
                entry_dict = entry.to_dict()
                entry_dict['id'] = entry.id
                # Convert datetime back to date string for frontend
                if entry_dict.get('date'):
                    if hasattr(entry_dict['date'], 'date'):
                        entry_dict['date'] = entry_dict['date'].date().isoformat()
                    else:
                        entry_dict['date'] = entry_dict['date'].isoformat() if hasattr(entry_dict['date'], 'isoformat') else str(entry_dict['date'])
                entries_data.append(entry_dict)
            
            return {
                'message': 'Daily data retrieved successfully',
                'data': entries_data,
                'total_count': len(entries_data)
            }, 200
            
        except Exception as e:
            logger.error(f"Get daily data error: {e}")
            return {'error': 'Internal server error'}, 500

@health_ns.route('/suggestion')
class HealthSuggestion(Resource):
    @jwt_required()
    @health_ns.marshal_with(success_response, code=200)
    @health_ns.response(401, 'Authentication required', error_response)
    @health_ns.response(503, 'AI service unavailable', error_response)
    def post(self):
        """Get daily health suggestion from AI"""
        try:
            user_id = get_jwt_identity()
            
            # Check if Gemini client is available
            if not genai_client:
                return {'error': 'Health suggestions are currently unavailable'}, 503
            
            # Check if user already got suggestion today using modern filter syntax
            today = datetime.now(timezone.utc).date()
            # Convert date to datetime for Firestore compatibility
            today_datetime = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            
            existing_suggestion = db.collection('health_suggestions').where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).where(
                filter=firestore.FieldFilter('date', '==', today_datetime)
            ).get()
            
            if existing_suggestion:
                return {
                    'message': '今日已使用',
                    'suggestion': existing_suggestion[0].to_dict()['suggestion'],
                    'already_received': True
                }, 200
            
            # Get user's recent entries for context using modern filter syntax
            entries_ref = db.collection('daily_entries').where(
                filter=firestore.FieldFilter('user_id', '==', user_id)
            ).order_by('date', direction=firestore.Query.DESCENDING).limit(7)
            recent_entries = entries_ref.get()
            
            # Get user profile
            user_doc = db.collection('users').document(user_id).get()
            user_data = user_doc.to_dict()
            
            # Prepare context for AI
            context = f"""
            User Profile:
            - Age: {datetime.now(timezone.utc).year - user_data.get('birth_date', datetime.now(timezone.utc)).year if user_data.get('birth_date') else 'Unknown'}
            - Initial Height: {user_data.get('initial_height', 'Unknown')} cm
            - Initial Weight: {user_data.get('initial_weight', 'Unknown')} kg
            
            Recent Entries (last 7 days):
            """
            
            for entry in recent_entries:
                entry_data = entry.to_dict()
                context += f"""
            - Date: {entry_data.get('date', 'Unknown')}
            - Height: {entry_data.get('height', 'Unknown')} cm
            - Weight: {entry_data.get('weight', 'Unknown')} kg
            - Meals: Breakfast: {entry_data.get('breakfast', 'Unknown')}, Lunch: {entry_data.get('lunch', 'Unknown')}, Dinner: {entry_data.get('dinner', 'Unknown')}
            """
            
            prompt = f"""
            {context}
            
            Based on this health data, provide a personalized, encouraging health suggestion for today. 
            Keep it concise (2-3 sentences), actionable, and positive. Focus on nutrition, exercise, or lifestyle tips.
            """
            
            # Generate suggestion using Gemini
            response = genai_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            suggestion = response.text
            
            # Store suggestion in database with datetime object
            suggestion_data = {
                'user_id': user_id,
                'date': today_datetime,  # Store as datetime object
                'suggestion': suggestion,
                'created_at': datetime.now(timezone.utc)
            }
            
            db.collection('health_suggestions').add(suggestion_data)
            
            return {
                'message': 'Daily suggestion generated successfully',
                'suggestion': suggestion,
                'already_received': False
            }, 200
            
        except Exception as e:
            logger.error(f"Health suggestion error: {e}")
            return {'error': 'Internal server error'}, 500

# Legacy endpoints for backward compatibility
@app.route('/register', methods=['POST'])
def register():
    """Legacy register endpoint"""
    return Register().post()

@app.route('/login', methods=['POST'])
def login():
    """Legacy login endpoint"""
    return Login().post()

@app.route('/submit_profile', methods=['POST'])
@jwt_required()
def submit_profile():
    """Legacy submit profile endpoint"""
    return Profile().post()

@app.route('/submit_daily_data', methods=['POST'])
@jwt_required()
def submit_daily_data():
    """Legacy submit daily data endpoint"""
    return DailyEntry().post()

@app.route('/get_daily_data', methods=['GET'])
@jwt_required()
def get_daily_data():
    """Legacy get daily data endpoint"""
    return DailyEntries().get()

@app.route('/get_daily_suggestion', methods=['POST'])
@jwt_required()
def get_daily_suggestion():
    """Legacy get daily suggestion endpoint"""
    return HealthSuggestion().post()

@app.route('/delete_account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """Legacy delete account endpoint"""
    return DeleteAccount().delete()

# Keep existing API endpoints for backward compatibility
@app.route('/api/register', methods=['POST'])
def api_register():
    return Register().post()

@app.route('/api/login', methods=['POST'])
def api_login():
    return Login().post()

@app.route('/api/profile', methods=['POST'])
@jwt_required()
def api_create_profile():
    return Profile().post()

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    return Profile().get()

@app.route('/api/daily-entry', methods=['POST'])
@jwt_required()
def api_create_daily_entry():
    return DailyEntry().post()

@app.route('/api/daily-entries', methods=['GET'])
@jwt_required()
def api_get_daily_entries():
    return DailyEntries().get()

@app.route('/api/health-suggestion', methods=['GET'])
@jwt_required()
def api_get_health_suggestion():
    return HealthSuggestion().post()

@app.route('/api/delete_account', methods=['DELETE'])
@jwt_required()
def api_delete_account():
    return DeleteAccount().delete()

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
