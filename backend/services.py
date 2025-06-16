from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import logging

from repositories import user_repo, daily_entry_repo, health_suggestion_repo
from utils import ai_service
from exceptions import (
    ValidationError, AuthenticationError, ConflictError, 
    NotFoundError, ServiceUnavailableError
)
from validators import Validator

logger = logging.getLogger(__name__)

class UserService:
    """User service for authentication and profile management"""
    
    @staticmethod
    def register_user(data: Dict[str, Any]) -> Dict[str, str]:
        """Register a new user"""
        # Validate input data
        validated_data = Validator.validate_registration_data(data)
        
        # Check if user already exists
        if user_repo.email_exists(validated_data['email']):
            raise ConflictError("Email already registered")
        
        if user_repo.username_exists(validated_data['username']):
            raise ConflictError("Username already taken")
        
        # Create user
        user_data = {
            'email': validated_data['email'],
            'username': validated_data['username'],
            'password': generate_password_hash(validated_data['password']),
            'created_at': datetime.now(timezone.utc),
            'profile_completed': False
        }
        
        user_id = user_repo.create(user_data)
        logger.info(f"User registered successfully: {validated_data['username']} ({user_id})")
        
        return {
            'user_id': user_id,
            'message': 'User registered successfully'
        }
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return token"""
        if not username or not password:
            raise ValidationError("Username and password required")
        
        # Find user by username or email
        user = None
        if '@' in username:
            user = user_repo.get_by_email(username.lower())
        else:
            user = user_repo.get_by_username(username)
        
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        # Verify password
        if not check_password_hash(user['password'], password):
            raise AuthenticationError("Invalid credentials")
        
        # Generate token
        access_token = create_access_token(identity=user['id'])
        
        logger.info(f"User authenticated successfully: {user['username']} ({user['id']})")
        
        return {
            'access_token': access_token,
            'user_id': user['id'],
            'profile_completed': user.get('profile_completed', False),
            'message': 'Login successful'
        }
    
    @staticmethod
    def get_user_profile(user_id: str) -> Dict[str, Any]:
        """Get user profile without sensitive data"""
        user = user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        logger.info(f"Raw user data from repository: {user}")
        
        # Remove sensitive information
        safe_profile = {k: v for k, v in user.items() if k != 'password'}
        
        # Ensure all required fields are present
        profile_fields = ['id', 'username', 'email', 'profile_completed', 'created_at']
        for field in profile_fields:
            if field not in safe_profile:
                logger.warning(f"Missing field {field} in user profile")
        
        logger.info(f"Safe profile data: {safe_profile}")
        return safe_profile
    
    @staticmethod
    def update_user_profile(user_id: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Update user profile"""
        # Validate input data
        validated_data = Validator.validate_profile_data(data)
        
        # Check if user exists
        if not user_repo.get_by_id(user_id):
            raise NotFoundError("User not found")
        
        # Update profile - validated_data already has datetime object
        profile_data = {
            'birth_date': validated_data['birth_date'],  # Already converted to datetime
            'initial_height': validated_data['initial_height'],
            'initial_weight': validated_data['initial_weight'],
            'profile_completed': True,
            'updated_at': datetime.now(timezone.utc)
        }
        
        user_repo.update(user_id, profile_data)
        logger.info(f"User profile updated: {user_id}")
        
        return {'message': 'Profile updated successfully'}
    
    @staticmethod
    def delete_user_account(user_id: str, password: str) -> Dict[str, str]:
        """Delete user account and all associated data"""
        # Get user for password verification
        user = user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Verify password
        if not check_password_hash(user['password'], password):
            raise AuthenticationError("Invalid password")
        
        # Delete associated data
        daily_count = daily_entry_repo.delete_by_user(user_id)
        suggestion_count = health_suggestion_repo.delete_by_user(user_id)
        
        # Delete user
        user_repo.delete(user_id)
        
        logger.info(f"User account deleted: {user_id} (entries: {daily_count}, suggestions: {suggestion_count})")
        
        return {'message': 'Account and all associated data deleted successfully'}

class HealthService:
    """Health service for daily data and AI suggestions"""
    
    @staticmethod
    def submit_daily_data(user_id: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Submit daily health data"""
        # Validate input data
        validated_data = Validator.validate_daily_data(data)
        
        # Check if entry already exists
        existing_entry = daily_entry_repo.get_by_user_and_date(user_id, validated_data['date'])
        if existing_entry:
            raise ConflictError("Entry already exists for this date")
        
        # Create entry - convert date to datetime for Firestore
        entry_data = {
            'user_id': user_id,
            'date': datetime.combine(validated_data['date'], datetime.min.time()),  # Convert to datetime
            'height': validated_data['height'],
            'weight': validated_data['weight'],
            'breakfast': validated_data['breakfast'],
            'lunch': validated_data['lunch'],
            'dinner': validated_data['dinner'],
            'created_at': datetime.now(timezone.utc)
        }
        
        entry_id = daily_entry_repo.create(entry_data)
        logger.info(f"Daily data submitted: {user_id} for {validated_data['date']}")
        
        return {
            'entry_id': entry_id,
            'message': 'Daily data submitted successfully'
        }
    
    @staticmethod
    def get_daily_data(user_id: str, limit: int = 30) -> Dict[str, Any]:
        """Get user's daily data entries"""
        entries = daily_entry_repo.get_by_user(user_id, limit)
        
        # Format dates for frontend
        for entry in entries:
            if entry.get('date'):
                if hasattr(entry['date'], 'date'):
                    entry['date'] = entry['date'].date().isoformat()
                elif hasattr(entry['date'], 'isoformat'):
                    entry['date'] = entry['date'].isoformat()
        
        return {
            'data': entries,
            'total_count': len(entries),
            'message': 'Daily data retrieved successfully'
        }
    
    @staticmethod
    def generate_health_suggestion(user_id: str) -> Dict[str, Any]:
        """Generate AI-powered health suggestion"""
        # Check if AI service is available
        if not ai_service.is_available():
            raise ServiceUnavailableError("Health suggestions are currently unavailable")
        
        today = datetime.now(timezone.utc).date()
        
        # Check if suggestion already exists for today
        existing_suggestion = health_suggestion_repo.get_by_user_and_date(user_id, today)
        if existing_suggestion:
            return {
                'suggestion': existing_suggestion['suggestion'],
                'already_received': True,
                'message': 'Daily suggestion already received'
            }
        
        # Get user profile and recent entries
        user = user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        recent_entries = daily_entry_repo.get_by_user(user_id, 7)
        
        # Generate suggestion
        suggestion = ai_service.generate_health_suggestion(user, recent_entries)
        
        # Store suggestion
        suggestion_data = {
            'user_id': user_id,
            'date': datetime.combine(today, datetime.min.time()),
            'suggestion': suggestion,
            'created_at': datetime.now(timezone.utc)
        }
        
        health_suggestion_repo.create(suggestion_data)
        logger.info(f"Health suggestion generated: {user_id}")
        
        return {
            'suggestion': suggestion,
            'already_received': False,
            'message': 'Daily suggestion generated successfully'
        }

# Service instances
user_service = UserService()
health_service = HealthService()
