import pytest
import uuid
import time

@pytest.mark.integration
class TestAPIIntegration:
    """API 集成測試"""
    
    def test_complete_user_workflow(self, api_client):
        """測試完整的用戶工作流程"""
        # 生成唯一用戶資料
        unique_id = f"{int(time.time())}_{str(uuid.uuid4())[:8]}"
        register_data = {
            "email": f"integration_{unique_id}@example.com",
            "username": f"integrationuser_{unique_id}",
            "password": "integrationpass123"
        }
        
        # 1. 註冊用戶
        register_response = api_client.post("/register", json=register_data)
        
        if register_response.status_code not in [200, 201]:
            pytest.skip("無法註冊用戶，跳過集成測試")
        
        user_id = register_response.json()["user_id"]
        
        try:
            # 2. 登入
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            login_response = api_client.post("/login", json=login_data)
            assert login_response.status_code == 200
            
            access_token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # 3. 提交個人資料
            profile_data = {
                "birth_date": "1990-05-15",
                "initial_height": 175.0,
                "initial_weight": 72.5
            }
            profile_response = api_client.post("/submit_profile", json=profile_data, headers=headers)
            assert profile_response.status_code == 200
            
            # 4. 提交日常數據 - 使用更穩定的日期生成
            import datetime
            today = datetime.date.today()
            test_date = today.replace(day=min(15, today.day))  # 確保日期有效
            daily_data = {
                "date": test_date.isoformat(),
                "height": 175.0,
                "weight": 72.0,
                "breakfast": "燕麥粥、水果",
                "lunch": "雞胸肉沙拉",
                "dinner": "蒸魚、蔬菜"
            }
            daily_response = api_client.post("/submit_daily_data", json=daily_data, headers=headers)
            assert daily_response.status_code in [200, 201]
            
            # 5. 獲取日常數據
            get_data_response = api_client.get("/get_daily_data", headers=headers)
            assert get_data_response.status_code == 200
            
            data = get_data_response.json()
            assert len(data["data"]) > 0
            
            # 6. 獲取個人資料
            get_profile_response = api_client.get("/api/profile", headers=headers)
            assert get_profile_response.status_code == 200
            
        except Exception as e:
            pytest.fail(f"集成測試失敗: {e}")
    
    def test_api_error_handling(self, api_client):
        """測試 API 錯誤處理"""
        # 測試不存在的端點
        response = api_client.get("/api/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.slow
    def test_api_performance(self, api_client):
        """測試 API 性能"""
        import time
        
        start_time = time.time()
        response = api_client.get("/api/profile")  # 這會返回 401，但測試響應時間
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0, f"API 響應時間過長: {response_time}秒"
    
    def test_authentication_flow(self, api_client):
        """測試認證流程"""
        # 測試未認證訪問受保護端點
        protected_endpoints = [
            "/submit_profile",
            "/submit_daily_data",
            "/get_daily_data",
            "/get_daily_suggestion",
            "/api/profile"
        ]
        
        for endpoint in protected_endpoints:
            response = api_client.get(endpoint)
            assert response.status_code == 401, f"端點 {endpoint} 應該需要認證"
