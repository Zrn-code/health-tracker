from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from google import genai
import os
import numpy as np
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Initialize extensions
CORS(app, origins=['http://localhost:5000', 'https://your-firebase-app.web.app'])
jwt = JWTManager(app)

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate('hello.json')
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase initialization error: {e}")

db = firestore.client()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize Gemini AI
api_key = os.environ.get('GEMINI_API_KEY')
if api_key:
    genai_client = genai.Client(api_key=api_key)
else:
    genai_client = None
    logger.warning("GEMINI_API_KEY not found - health suggestions will be disabled")






@app.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists using modern filter syntax
        users_ref = db.collection('users')
        existing_user = users_ref.where(filter=firestore.FieldFilter('email', '==', data['email'])).get()
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Check if username already exists
        existing_username = users_ref.where(filter=firestore.FieldFilter('username', '==', data['username'])).get()
        if existing_username:
            return jsonify({'error': 'Username already exists'}), 409
        
        # Create new user
        hashed_password = generate_password_hash(data['password'])
        user_data = {
            'email': data['email'],
            'username': data['username'],
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'profile_completed': False
        }
        
        doc_ref = users_ref.add(user_data)
        user_id = doc_ref[1].id
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        # Find user by username using modern filter syntax
        users_ref = db.collection('users')
        user_docs = users_ref.where(filter=firestore.FieldFilter('username', '==', data['username'])).get()
        
        if not user_docs:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_doc = user_docs[0]
        user_data = user_doc.to_dict()
        
        # Verify password
        if not check_password_hash(user_data['password'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        access_token = create_access_token(identity=user_doc.id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user_id': user_doc.id,
            'profile_completed': user_data.get('profile_completed', False)
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/submit_profile', methods=['POST'])
@jwt_required()
def submit_profile():
    """Submit user profile endpoint"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['birth_date', 'initial_height', 'initial_weight']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Update user profile
        profile_data = {
            'birth_date': datetime.strptime(data['birth_date'], '%Y-%m-%d'),
            'initial_height': float(data['initial_height']),
            'initial_weight': float(data['initial_weight']),
            'profile_completed': True,
            'updated_at': datetime.utcnow()
        }
        
        db.collection('users').document(user_id).update(profile_data)
        
        return jsonify({
            'message': 'Profile submitted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Profile submission error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/submit_daily_data', methods=['POST'])
@jwt_required()
def submit_daily_data():
    """Submit daily data endpoint"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'height', 'weight', 'breakfast', 'lunch', 'dinner']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Parse date
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Check if entry already exists for this date using modern filter syntax
        existing_entry = db.collection('daily_entries').where(
            filter=firestore.FieldFilter('user_id', '==', user_id)
        ).where(
            filter=firestore.FieldFilter('date', '==', entry_date)
        ).get()
        
        if existing_entry:
            return jsonify({'error': 'Entry already exists for this date'}), 409
        
        # Create daily entry
        entry_data = {
            'user_id': user_id,
            'date': entry_date,
            'height': float(data['height']),
            'weight': float(data['weight']),
            'breakfast': data['breakfast'],
            'lunch': data['lunch'],
            'dinner': data['dinner'],
            'created_at': datetime.utcnow()
        }
        
        doc_ref = db.collection('daily_entries').add(entry_data)
        
        return jsonify({
            'message': 'Daily data submitted successfully',
            'entry_id': doc_ref[1].id
        }), 201
        
    except Exception as e:
        logger.error(f"Daily data submission error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/get_daily_data', methods=['GET'])
@jwt_required()
def get_daily_data():
    """Get user's daily data endpoint"""
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
            entry_dict['date'] = entry_dict['date'].isoformat() if entry_dict.get('date') else None
            entries_data.append(entry_dict)
        
        return jsonify({
            'message': 'Daily data retrieved successfully',
            'data': entries_data,
            'total_count': len(entries_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Get daily data error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/get_daily_suggestion', methods=['POST'])
@jwt_required()
def get_daily_suggestion():
    """Get daily health suggestion from Gemini AI"""
    try:
        user_id = get_jwt_identity()
        
        # Check if Gemini client is available
        if not genai_client:
            return jsonify({'error': 'Health suggestions are currently unavailable'}), 503
        
        # Check if user already got suggestion today using modern filter syntax
        today = datetime.utcnow().date()
        existing_suggestion = db.collection('health_suggestions').where(
            filter=firestore.FieldFilter('user_id', '==', user_id)
        ).where(
            filter=firestore.FieldFilter('date', '==', today)
        ).get()
        
        if existing_suggestion:
            return jsonify({
                'message': '今日已使用',
                'suggestion': existing_suggestion[0].to_dict()['suggestion'],
                'already_received': True
            }), 200
        
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
        - Age: {datetime.utcnow().year - user_data.get('birth_date', datetime.utcnow()).year if user_data.get('birth_date') else 'Unknown'}
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
        
        # Store suggestion in database
        suggestion_data = {
            'user_id': user_id,
            'date': today,
            'suggestion': suggestion,
            'created_at': datetime.utcnow()
        }
        
        db.collection('health_suggestions').add(suggestion_data)
        
        return jsonify({
            'message': 'Daily suggestion generated successfully',
            'suggestion': suggestion,
            'already_received': False
        }), 200
        
    except Exception as e:
        logger.error(f"Health suggestion error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Keep existing endpoints for backward compatibility
@app.route('/api/register', methods=['POST'])
def api_register():
    return register()

@app.route('/api/login', methods=['POST'])
def api_login():
    return login()

@app.route('/api/profile', methods=['POST'])
@jwt_required()
def api_create_profile():
    return submit_profile()

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_doc.to_dict()
        
        # Remove sensitive information
        user_data.pop('password', None)
        
        return jsonify(user_data), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/daily-entry', methods=['POST'])
@jwt_required()
def api_create_daily_entry():
    return submit_daily_data()

@app.route('/api/daily-entries', methods=['GET'])
@jwt_required()
def api_get_daily_entries():
    return get_daily_data()

@app.route('/api/health-suggestion', methods=['GET'])
@jwt_required()
def api_get_health_suggestion():
    return get_daily_suggestion()

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
