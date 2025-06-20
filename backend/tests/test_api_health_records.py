import pytest
from datetime import datetime, date
import uuid
import time

@pytest.mark.api
class TestDailyDataAPI:
    """日常數據 API 測試"""
    
    def setup_authenticated_user(self, api_client):
        """設置已認證的用戶"""
        # 生成唯一用戶數據
        unique_id = f"{int(time.time())}_{str(uuid.uuid4())[:8]}"
        unique_user_data = {
            "email": f"dailytest_{unique_id}@example.com",
            "username": f"dailyuser_{unique_id}",
            "password": "dailypass123"
        }
        
        # 註冊用戶
        register_response = api_client.post("/api/auth/register", json=unique_user_data)
        
        if register_response.status_code not in [200, 201]:
            return None
        
        # 登入獲取 token
        login_data = {
            "username": unique_user_data["username"],
            "password": unique_user_data["password"]
        }
        login_response = api_client.post("/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            return None
        
        # 返回 token 和用戶數據，以便清理
        return {
            'token': login_response.json()["access_token"],
            'user_data': unique_user_data
        }
    
    def test_submit_daily_data_missing_fields(self, api_client):
        """測試提交缺少必要欄位的日常數據"""
        auth_result = self.setup_authenticated_user(api_client)
        if not auth_result:
            pytest.skip("無法設置認證用戶")
        
        invalid_data = {
            "date": "2024-01-15",
            "height": 170.5
            # 缺少 weight, breakfast, lunch, dinner
        }
        
        headers = {"Authorization": f"Bearer {auth_result['token']}"}
        response = api_client.post("/api/health/daily-entry", json_data=invalid_data, headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "message" in data
        
        # Clean up
        self._cleanup_test_user(api_client, auth_result['token'])
    
    def test_submit_daily_data_success(self, api_client):
        """測試提交日常數據"""
        auth_result = self.setup_authenticated_user(api_client)
        if not auth_result:
            pytest.skip("無法設置認證用戶")
        
        # 使用更穩定的日期生成方法
        import datetime
        today = datetime.date.today()
        # 使用當前時間的秒數來生成一個1-28之間的日期，確保在所有月份都有效
        day = (int(time.time()) % 28) + 1
        test_date = today.replace(day=day)
        
        daily_data = {
            "date": test_date.isoformat(),
            "height": 170.5,
            "weight": 70.5,
            "breakfast": "燕麥粥、牛奶",
            "lunch": "雞胸肉沙拉",
            "dinner": "蒸魚、青菜"
        }
        
        headers = {"Authorization": f"Bearer {auth_result['token']}"}
        response = api_client.post("/api/health/daily-entry", json=daily_data, headers=headers)
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "entry_id" in data
        assert data["message"] == "Daily data submitted successfully"
        
        # Clean up test user
        self._cleanup_test_user(api_client, auth_result['token'])
    
    def test_get_daily_data_success(self, api_client):
        """測試獲取日常數據"""
        auth_result = self.setup_authenticated_user(api_client)
        if not auth_result:
            pytest.skip("無法設置認證用戶")
        
        headers = {"Authorization": f"Bearer {auth_result['token']}"}
        response = api_client.get("/api/health/daily-entries", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total_count" in data
        assert isinstance(data["data"], list)
        
        # Clean up
        self._cleanup_test_user(api_client, auth_result['token'])
    
    def test_get_daily_data_unauthorized(self, api_client):
        """測試未授權訪問日常數據"""
        response = api_client.get("/api/health/daily-entries")
        assert response.status_code == 401
    
    def test_get_health_suggestion(self, api_client):
        """測試獲取健康建議"""
        auth_result = self.setup_authenticated_user(api_client)
        if not auth_result:
            pytest.skip("無法設置認證用戶")
        
        headers = {"Authorization": f"Bearer {auth_result['token']}"}
        response = api_client.post("/api/health/suggestion", headers=headers)
        
        # 可能返回 200（成功）或 503（服務不可用）
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "suggestion" in data
        
        # Clean up
        self._cleanup_test_user(api_client, auth_result['token'])
    
    def _cleanup_test_user(self, api_client, access_token):
        """清理測試用戶"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            # 假設我們有默認密碼用於測試清理
            delete_data = {"password": "dailypass123"}
            api_client.delete("/api/profile/delete", json=delete_data, headers=headers)
        except:
            # 如果清理失敗，忽略錯誤
            pass
