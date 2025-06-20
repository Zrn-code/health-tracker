import pytest
import uuid
import time
import json
from typing import Dict, Any, Optional

# Import the Flask app
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def generate_unique_id():
    """生成唯一標識符"""
    timestamp = str(int(time.time()))
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"

class FlaskTestClient:
    """Flask test client wrapper"""
    
    def __init__(self, app):
        self.app = app
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def is_server_available(self) -> bool:
        """Always return True for Flask test client"""
        return True
    
    def _process_response(self, response):
        """Process Flask test response to match requests response format"""
        class MockResponse:
            def __init__(self, flask_response):
                self.status_code = flask_response.status_code
                self.text = flask_response.get_data(as_text=True)
                self._json_data = None
                self._flask_response = flask_response
            
            def json(self):
                if self._json_data is None:
                    try:
                        self._json_data = json.loads(self.text)
                    except (json.JSONDecodeError, ValueError):
                        self._json_data = {}
                return self._json_data
        
        return MockResponse(response)
    
    def get(self, endpoint, headers=None, **kwargs):
        """GET request"""
        response = self.client.get(endpoint, headers=headers, **kwargs)
        return self._process_response(response)
    
    def post(self, endpoint, data=None, json_data=None, headers=None, **kwargs):
        """POST request"""
        if json_data is not None:
            data = json.dumps(json_data)
            if headers is None:
                headers = {}
            headers['Content-Type'] = 'application/json'
        
        response = self.client.post(
            endpoint, 
            data=data,
            headers=headers,
            **kwargs
        )
        return self._process_response(response)
    
    def put(self, endpoint, data=None, json_data=None, headers=None, **kwargs):
        """PUT request"""
        if json_data is not None:
            data = json.dumps(json_data)
            if headers is None:
                headers = {}
            headers['Content-Type'] = 'application/json'
        
        response = self.client.put(
            endpoint,
            data=data,
            headers=headers,
            **kwargs
        )
        return self._process_response(response)
    
    def delete(self, endpoint, data=None, json_data=None, headers=None, **kwargs):
        """DELETE request"""
        if json_data is not None:
            data = json.dumps(json_data)
            if headers is None:
                headers = {}
            headers['Content-Type'] = 'application/json'
        
        response = self.client.delete(
            endpoint,
            data=data,
            headers=headers,
            **kwargs
        )
        return self._process_response(response)
    
    def cleanup(self):
        """Clean up app context"""
        self.app_context.pop()

@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app('testing')  # Use testing configuration
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def api_client(app):
    """提供 Flask test client"""
    client = FlaskTestClient(app)
    yield client
    client.cleanup()

@pytest.fixture
def server_available():
    """Always return True for Flask test client"""
    return True

@pytest.fixture(scope="function")
def unique_user_data():
    """生成唯一的測試用戶數據"""
    unique_id = generate_unique_id()
    timestamp = str(int(time.time()))
    return {
        "email": f"email_{unique_id}@example.com",
        "username": f"user_{timestamp}_{unique_id[:8]}",
        "password": "testpassword123"
    }

@pytest.fixture(scope="function")
def unique_profile_data():
    """生成唯一的測試個人資料數據"""
    return {
        "birth_date": "1990-01-01",
        "initial_height": 170.0,
        "initial_weight": 70.0
    }

def get_unique_user_data():
    """Get unique user data for testing"""
    unique_id = generate_unique_id()
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "testpassword123"
    }
# Export unique_user_data function for direct import
def get_unique_user_data():
    """Get unique user data for testing"""
    unique_id = generate_unique_id()
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "testpassword123"
    }

