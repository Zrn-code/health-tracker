import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from werkzeug.security import generate_password_hash

from services import UserService, HealthService
from exceptions import ValidationError, ConflictError, AuthenticationError, NotFoundError, ServiceUnavailableError

class TestUserService:
    """Test UserService class"""
    
    @patch('services.user_repo')
    def test_register_user_success(self, mock_user_repo):
        """Test successful user registration"""
        # Setup mocks
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.username_exists.return_value = False
        mock_user_repo.create.return_value = 'user123'
        
        # Test data
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        }
        
        # Execute
        result = UserService.register_user(data)
        
        # Verify
        assert result['user_id'] == 'user123'
        assert result['message'] == 'User registered successfully'
        mock_user_repo.create.assert_called_once()
    
    @patch('services.user_repo')
    def test_register_user_email_exists(self, mock_user_repo):
        """Test registration with existing email"""
        mock_user_repo.email_exists.return_value = True
        
        data = {
            'email': 'existing@example.com',
            'username': 'testuser',
            'password': 'password123'
        }
        
        with pytest.raises(ConflictError) as exc_info:
            UserService.register_user(data)
        
        assert "Email already registered" in str(exc_info.value)
    
    @patch('services.user_repo')
    def test_authenticate_user_success(self, mock_user_repo):
        """Test successful user authentication"""
        # Setup mock user
        hashed_password = generate_password_hash('password123')
        mock_user = {
            'id': 'user123',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': hashed_password,
            'profile_completed': True
        }
        mock_user_repo.get_by_username.return_value = mock_user
        
        # Execute
        with patch('services.create_access_token') as mock_create_token:
            mock_create_token.return_value = 'mock_token'
            result = UserService.authenticate_user('testuser', 'password123')
        
        # Verify
        assert result['access_token'] == 'mock_token'
        assert result['user_id'] == 'user123'
        assert result['profile_completed'] is True
    
    def test_authenticate_user_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        with pytest.raises(ValidationError):
            UserService.authenticate_user('', 'password')
        
        with pytest.raises(ValidationError):
            UserService.authenticate_user('username', '')

class TestHealthService:
    """Test HealthService class"""
    
    @patch('services.daily_entry_repo')
    def test_submit_daily_data_success(self, mock_daily_repo):
        """Test successful daily data submission"""
        # Setup mocks
        mock_daily_repo.get_by_user_and_date.return_value = None
        mock_daily_repo.create.return_value = 'entry123'
        
        # Test data
        data = {
            'date': '2024-01-15',
            'height': 175.0,
            'weight': 70.5,
            'breakfast': 'Oatmeal',
            'lunch': 'Salad',
            'dinner': 'Fish'
        }
        
        # Execute
        result = HealthService.submit_daily_data('user123', data)
        
        # Verify
        assert result['entry_id'] == 'entry123'
        assert result['message'] == 'Daily data submitted successfully'
        mock_daily_repo.create.assert_called_once()
    
    @patch('services.daily_entry_repo')
    def test_submit_daily_data_duplicate(self, mock_daily_repo):
        """Test submission with duplicate date"""
        mock_daily_repo.get_by_user_and_date.return_value = {'id': 'existing'}
        
        data = {
            'date': '2024-01-15',
            'height': 175.0,
            'weight': 70.5,
            'breakfast': 'Oatmeal',
            'lunch': 'Salad',
            'dinner': 'Fish'
        }
        
        with pytest.raises(ConflictError) as exc_info:
            HealthService.submit_daily_data('user123', data)
        
        assert "Entry already exists for this date" in str(exc_info.value)
    
    @patch('services.ai_service')
    @patch('services.health_suggestion_repo')
    @patch('services.user_repo')
    @patch('services.daily_entry_repo')
    def test_generate_health_suggestion_success(self, mock_daily_repo, mock_user_repo, 
                                                mock_suggestion_repo, mock_ai_service):
        """Test successful health suggestion generation"""
        # Setup mocks
        mock_ai_service.is_available.return_value = True
        mock_suggestion_repo.get_by_user_and_date.return_value = None
        mock_user_repo.get_by_id.return_value = {'id': 'user123', 'birth_date': date(1990, 1, 1)}
        mock_daily_repo.get_by_user.return_value = []
        mock_ai_service.generate_health_suggestion.return_value = "Drink more water today!"
        mock_suggestion_repo.create.return_value = 'suggestion123'
        
        # Execute
        result = HealthService.generate_health_suggestion('user123')
        
        # Verify
        assert result['suggestion'] == "Drink more water today!"
        assert result['already_received'] is False
        mock_suggestion_repo.create.assert_called_once()
    
    @patch('services.ai_service')
    def test_generate_health_suggestion_service_unavailable(self, mock_ai_service):
        """Test health suggestion when AI service is unavailable"""
        mock_ai_service.is_available.return_value = False
        
        with pytest.raises(ServiceUnavailableError):
            HealthService.generate_health_suggestion('user123')
    
    @patch('services.ai_service')
    @patch('services.health_suggestion_repo')
    def test_generate_health_suggestion_already_received(self, mock_suggestion_repo, mock_ai_service):
        """Test health suggestion when user already received one today"""
        mock_ai_service.is_available.return_value = True
        mock_suggestion_repo.get_by_user_and_date.return_value = {'id': 'existing', 'suggestion': 'Previous suggestion'}
        
        result = HealthService.generate_health_suggestion('user123')
        
        assert result['suggestion'] == 'Previous suggestion'
        assert result['already_received'] is True
        mock_suggestion_repo.create.assert_not_called()
    
    @patch('services.daily_entry_repo')
    def test_get_daily_data_success(self, mock_daily_repo):
        """Test successful retrieval of daily data"""
        mock_entries = [
            {'id': 1, 'date': '2024-01-15', 'weight': 70.0},
            {'id': 2, 'date': '2024-01-14', 'weight': 70.5}
        ]
        mock_daily_repo.get_by_user.return_value = mock_entries
        mock_daily_repo.count_by_user.return_value = 2
        
        result = HealthService.get_daily_data('user123', 10)
        
        assert result['data'] == mock_entries
        assert result['total_count'] == 2

        mock_daily_repo.get_by_user.assert_called_once_with('user123', 10)
    
    @patch('services.daily_entry_repo')
    def test_get_daily_data_empty(self, mock_daily_repo):
        """Test retrieval when no daily data exists"""
        mock_daily_repo.get_by_user.return_value = []
        mock_daily_repo.count_by_user.return_value = 0
        
        result = HealthService.get_daily_data('user123', 10)
        
        assert result['data'] == []
        assert result['total_count'] == 0

    def test_submit_daily_data_validation_error(self):
        """Test daily data submission with validation errors"""
        with pytest.raises(ValidationError):
            HealthService.submit_daily_data('user123', {})  # Empty data
        
        with pytest.raises(ValidationError):
            HealthService.submit_daily_data('user123', {'date': 'invalid-date'})  # Invalid date format
