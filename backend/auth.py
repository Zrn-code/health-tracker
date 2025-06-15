from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from logger import get_logger, log_auth_attempt, log_registration_attempt, log_user_action
from models import db_instance

logger = get_logger('auth')
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        existing_user = db_instance.get_user_by_email(data['email'])
        if existing_user:
            log_registration_attempt(data['email'], data['username'], False, 'Email already registered')
            return jsonify({'error': 'Email already registered'}), 409
        
        # Check if username already exists
        existing_username = db_instance.get_user_by_username(data['username'])
        if existing_username:
            log_registration_attempt(data['email'], data['username'], False, 'Username already taken')
            return jsonify({'error': 'Username already taken'}), 409
        
        # Create new user
        hashed_password = generate_password_hash(data['password'])
        user_data = {
            'email': data['email'],
            'username': data['username'],
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'profile_completed': False
        }
        
        doc_ref = db_instance.create_user(user_data)
        user_id = doc_ref[1].id
        
        log_registration_attempt(data['email'], data['username'], True)
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        # Find user by username
        user_docs = db_instance.get_user_by_username(data['username'])
        
        if not user_docs:
            log_auth_attempt(data['username'], False, 'User not found')
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_doc = user_docs[0]
        user_data = user_doc.to_dict()
        
        # Verify password
        if not check_password_hash(user_data['password'], data['password']):
            log_auth_attempt(data['username'], False, 'Invalid password')
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        access_token = create_access_token(identity=user_doc.id)
        
        log_auth_attempt(data['username'], True)
        log_user_action(user_doc.id, 'LOGIN', f'User {data["username"]} logged in')
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user_id': user_doc.id,
            'profile_completed': user_data.get('profile_completed', False)
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        user_doc = db_instance.get_user_by_id(user_id)
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_doc.to_dict()
        
        # Remove sensitive information
        user_data.pop('password', None)
        
        return jsonify(user_data), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['POST'])
@auth_bp.route('/submit_profile', methods=['POST'])
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
        
        db_instance.update_user(user_id, profile_data)
        
        log_user_action(user_id, 'PROFILE_UPDATED', 'User completed profile setup')
        
        return jsonify({
            'message': 'Profile submitted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Profile submission error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
