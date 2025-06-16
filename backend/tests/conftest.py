import pytest
import requests
from typing import Dict, Any
import json
import uuid
import time

# 測試配置
TEST_CONFIG = {
    "base_url": "http://localhost:5000",
    "timeout": 10,
    "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
}

def generate_unique_id():
    """生成唯一標識符"""
    timestamp = str(int(time.time()))
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"

@pytest.fixture(scope="session")
def api_client():
    """創建 API 客戶端 fixture"""
    class APIClient:
        def __init__(self, base_url: str, headers: Dict[str, str]):
            self.base_url = base_url
            self.session = requests.Session()
            self.session.headers.update(headers)
            
        def _make_request(self, method: str, endpoint: str, **kwargs):
            """統一的請求處理方法"""
            url = f"{self.base_url}{endpoint}"
            request_headers = self.session.headers.copy()
            if 'headers' in kwargs:
                request_headers.update(kwargs.pop('headers'))
            
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    timeout=TEST_CONFIG["timeout"],
                    **kwargs
                )
                return response
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {method} {url} - {e}")
                raise
            
        def get(self, endpoint: str, params=None, headers=None, **kwargs):
            return self._make_request('GET', endpoint, params=params, headers=headers, **kwargs)
            
        def post(self, endpoint: str, data=None, json=None, headers=None, **kwargs):
            return self._make_request('POST', endpoint, data=data, json=json, headers=headers, **kwargs)
            
        def put(self, endpoint: str, data=None, json=None, headers=None, **kwargs):
            return self._make_request('PUT', endpoint, data=data, json=json, headers=headers, **kwargs)
            
        def delete(self, endpoint: str, json=None, headers=None, **kwargs):
            return self._make_request('DELETE', endpoint, json=json, headers=headers, **kwargs)
            
        def patch(self, endpoint: str, data=None, json=None, headers=None, **kwargs):
            return self._make_request('PATCH', endpoint, data=data, json=json, headers=headers, **kwargs)
    
    return APIClient(TEST_CONFIG["base_url"], TEST_CONFIG["headers"])

@pytest.fixture(scope="function")
def unique_user_data():
    """生成唯一的測試用戶數據"""
    unique_id = generate_unique_id()
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
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
    return APIClient(TEST_CONFIG["base_url"], TEST_CONFIG["headers"])

@pytest.fixture(scope="function")
def unique_user_data():
    """生成唯一的測試用戶數據"""
    unique_id = generate_unique_id()
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
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
