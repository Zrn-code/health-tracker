from typing import Dict, Any
from datetime import datetime, date
import re
from exceptions import ValidationError

class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_registration_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user registration data"""
        required_fields = ['email', 'username', 'password']
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"Field '{field}' is required", field)
        
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            raise ValidationError("Invalid email format", 'email')
        
        # Validate username (no @ symbol allowed)
        if '@' in data['username']:
            raise ValidationError("Username cannot contain @ symbol", 'username')
        
        # Validate password length
        if len(data['password']) < 6:
            raise ValidationError("Password must be at least 6 characters long", 'password')
        
        return {
            'email': data['email'].lower().strip(),
            'username': data['username'].strip(),
            'password': data['password']
        }
    
    @staticmethod
    def validate_profile_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user profile data"""
        required_fields = ['birth_date', 'initial_height', 'initial_weight']
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"Field '{field}' is required", field)
        
        # Validate and convert birth_date
        birth_date = data['birth_date']
        if isinstance(birth_date, str):
            try:
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Invalid birth date format. Use YYYY-MM-DD", 'birth_date')
        elif isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        elif not isinstance(birth_date, date):
            raise ValidationError("Invalid birth date type", 'birth_date')
        
        # Convert date to datetime for Firestore compatibility
        birth_datetime = datetime.combine(birth_date, datetime.min.time())
        
        # Validate height
        try:
            height = float(data['initial_height'])
            if height < 50 or height > 300:
                raise ValidationError("Height must be between 50 and 300 cm", 'initial_height')
        except (ValueError, TypeError):
            raise ValidationError("Invalid height value", 'initial_height')
        
        # Validate weight
        try:
            weight = float(data['initial_weight'])
            if weight < 20 or weight > 500:
                raise ValidationError("Weight must be between 20 and 500 kg", 'initial_weight')
        except (ValueError, TypeError):
            raise ValidationError("Invalid weight value", 'initial_weight')
        
        return {
            'birth_date': birth_datetime,  # Store as datetime for Firestore
            'initial_height': height,
            'initial_weight': weight
        }
    
    @staticmethod
    def validate_daily_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate daily health data"""
        required_fields = ['date', 'height', 'weight', 'breakfast', 'lunch', 'dinner']
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"Field '{field}' is required", field)
        
        # Validate and convert date
        entry_date = data['date']
        if isinstance(entry_date, str):
            try:
                entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD", 'date')
        elif isinstance(entry_date, datetime):
            entry_date = entry_date.date()
        elif not isinstance(entry_date, date):
            raise ValidationError("Invalid date type", 'date')
        
        # Validate height
        try:
            height = float(data['height'])
            if height < 50 or height > 300:
                raise ValidationError("Height must be between 50 and 300 cm", 'height')
        except (ValueError, TypeError):
            raise ValidationError("Invalid height value", 'height')
        
        # Validate weight
        try:
            weight = float(data['weight'])
            if weight < 20 or weight > 500:
                raise ValidationError("Weight must be between 20 and 500 kg", 'weight')
        except (ValueError, TypeError):
            raise ValidationError("Invalid weight value", 'weight')
        
        # Validate meal descriptions
        for meal in ['breakfast', 'lunch', 'dinner']:
            if len(data[meal].strip()) < 1:
                raise ValidationError(f"{meal.capitalize()} description is required", meal)
        
        return {
            'date': entry_date,  # Keep as date for now, will convert in service
            'height': height,
            'weight': weight,
            'breakfast': data['breakfast'].strip(),
            'lunch': data['lunch'].strip(),
            'dinner': data['dinner'].strip()
        }
