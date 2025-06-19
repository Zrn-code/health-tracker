import pytest
import requests
import uuid
import time
from typing import Dict, Any, Optional

# 測試配置
TEST_CONFIG = {
    "base_url": "http://localhost:8080",
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

def check_server_availability(base_url: str = "http://localhost:8080") -> bool:
    """檢查服務器是否可用"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        try:
            # 嘗試根路徑
            response = requests.get(base_url, timeout=5)
            return response.status_code in [200, 404]  # 404也算服務器在運行
        except:
            return False

class APIClient:
    """API client for testing"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self._server_available = None
    
    def is_server_available(self) -> bool:
        """檢查服務器是否可用"""
        if self._server_available is None:
            self._server_available = check_server_availability(self.base_url)
        return self._server_available
    
    def _make_request(self, method, endpoint, data=None, json=None, headers=None, **kwargs):
        """發送HTTP請求的通用方法"""
        url = f"{self.base_url}{endpoint}"
        
        # 設置默認請求頭
        request_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # 如果有額外的請求頭，則合併
        if headers:
            request_headers.update(headers)
        
        # 從kwargs中安全地獲取headers
        additional_headers = kwargs.pop('headers', None)
        if additional_headers:
            request_headers.update(additional_headers)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=30,
                **kwargs
            )
            return response
        except requests.exceptions.ConnectionError:
            # 連接錯誤 - 服務器可能未運行
            class MockResponse:
                def __init__(self):
                    self.status_code = 503
                    self.text = "Service Unavailable - Server not running"
                
                def json(self):
                    return {"message": "Service Unavailable - Server not running"}
            
            return MockResponse()
        except requests.exceptions.Timeout:
            # 超時錯誤
            class MockResponse:
                def __init__(self):
                    self.status_code = 408
                    self.text = "Request Timeout"
                
                def json(self):
                    return {"message": "Request Timeout"}
            
            return MockResponse()
        except requests.exceptions.RequestException as e:
            # 其他請求錯誤
            class MockResponse:
                def __init__(self):
                    self.status_code = 500
                    self.text = f"Request Error: {str(e)}"
                
                def json(self):
                    return {"message": f"Request Error: {str(e)}"}
            
            return MockResponse()
    
    def get(self, endpoint, headers=None, **kwargs):
        return self._make_request('GET', endpoint, headers=headers, **kwargs)
    
    def post(self, endpoint, data=None, json=None, headers=None, **kwargs):
        return self._make_request('POST', endpoint, data=data, json=json, headers=headers, **kwargs)
    
    def put(self, endpoint, data=None, json=None, headers=None, **kwargs):
        return self._make_request('PUT', endpoint, data=data, json=json, headers=headers, **kwargs)
    
    def delete(self, endpoint, data=None, json=None, headers=None, **kwargs):
        return self._make_request('DELETE', endpoint, data=data, json=json, headers=headers, **kwargs)

@pytest.fixture
def api_client():
    """提供 API 客戶端"""
    return APIClient()

@pytest.fixture
def server_available(api_client):
    """檢查服務器是否可用的 fixture"""
    return api_client.is_server_available()

@pytest.fixture(scope="function")
def unique_user_data():
    """生成唯一的測試用戶數據"""
    unique_id = generate_unique_id()
    timestamp = str(int(time.time()))
    # 確保 email 和 username 不同
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

# Export unique_user_data function for direct import
def get_unique_user_data():
    """Get unique user data for testing"""
    unique_id = generate_unique_id()
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "testpassword123"
    }

