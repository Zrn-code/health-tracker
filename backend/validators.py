import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from exceptions import ValidationError

class Validator:
    """Input validation utility class"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        if not email or not isinstance(email, str):
            raise ValidationError("Email is required", "email")
        
        email = email.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Invalid email format", "email")
        
        return email
    
    @staticmethod
    def validate_username(username: str) -> str:
        """Validate username format"""
        if not username or not isinstance(username, str):
            raise ValidationError("Username is required", "username")
        
        username = username.strip()
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters", "username")
        
        if len(username) > 50:
            raise ValidationError("Username must not exceed 50 characters", "username")
        
        if '@' in username:
            raise ValidationError("Username cannot contain @ symbol", "username")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationError("Username can only contain letters, numbers, hyphens and underscores", "username")
        
        return username
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if not password or not isinstance(password, str):
            raise ValidationError("Password is required", "password")
        
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters", "password")
        
        if len(password) > 128:
            raise ValidationError("Password must not exceed 128 characters", "password")
        
        return password
    
    @staticmethod
    def validate_date(date_str: str, field_name: str = "date") -> date:
        """Validate date format (YYYY-MM-DD)"""
        if not date_str or not isinstance(date_str, str):
            raise ValidationError(f"{field_name.title()} is required", field_name)
        
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError(f"Invalid {field_name} format. Use YYYY-MM-DD", field_name)
    
    @staticmethod
    def validate_positive_number(value: Any, field_name: str, min_value: float = 0.1, max_value: float = 1000.0) -> float:
        """Validate positive number within range"""
        if value is None:
            raise ValidationError(f"{field_name.title()} is required", field_name)
        
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name.title()} must be a number", field_name)
        
        if num_value < min_value:
            raise ValidationError(f"{field_name.title()} must be at least {min_value}", field_name)
        
        if num_value > max_value:
            raise ValidationError(f"{field_name.title()} must not exceed {max_value}", field_name)
        
        return num_value
    
    @staticmethod
    def validate_required_string(value: str, field_name: str, max_length: int = 500) -> str:
        """Validate required string field"""
        if not value or not isinstance(value, str):
            raise ValidationError(f"{field_name.title()} is required", field_name)
        
        value = value.strip()
        if not value:
            raise ValidationError(f"{field_name.title()} cannot be empty", field_name)
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name.title()} must not exceed {max_length} characters", field_name)
        
        return value
    
    @staticmethod
    def validate_registration_data(data: Dict[str, Any]) -> Dict[str, str]:
        """Validate user registration data"""
        return {
            'email': Validator.validate_email(data.get('email')),
            'username': Validator.validate_username(data.get('username')),
            'password': Validator.validate_password(data.get('password'))
        }
    
    @staticmethod
    def validate_profile_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user profile data"""
        return {
            'birth_date': Validator.validate_date(data.get('birth_date'), 'birth_date'),
            'initial_height': Validator.validate_positive_number(data.get('initial_height'), 'height', 50.0, 300.0),
            'initial_weight': Validator.validate_positive_number(data.get('initial_weight'), 'weight', 20.0, 500.0)
        }
    
    @staticmethod
    def validate_daily_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate daily health data"""
        return {
            'date': Validator.validate_date(data.get('date')),
            'height': Validator.validate_positive_number(data.get('height'), 'height', 50.0, 300.0),
            'weight': Validator.validate_positive_number(data.get('weight'), 'weight', 20.0, 500.0),
            'breakfast': Validator.validate_required_string(data.get('breakfast'), 'breakfast'),
            'lunch': Validator.validate_required_string(data.get('lunch'), 'lunch'),
            'dinner': Validator.validate_required_string(data.get('dinner'), 'dinner')
        }
