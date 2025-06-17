import pytest
import requests
from requests.exceptions import RequestException, ConnectionError
import json

from conftest import unique_user_data

@pytest.mark.api
class TestUsersAPI:
    """用戶 API 測試"""
    BASE_URL = "http://localhost:5000"
    
    def is_server_available(self):
        """檢查服務器是否可用"""
        try:
            response = requests.get(f"{self.BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except (RequestException, ConnectionError):
            return False
    
    def test_register_user_success(self, api_client, unique_user_data, server_available):
        """測試用戶註冊"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        response = api_client.post("/api/auth/register", json=unique_user_data)
        
        if response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "user_id" in data
        assert data["message"] == "User registered successfully"
        
        # Clean up - delete the test account
        self._cleanup_user(api_client, unique_user_data)
    
    def test_register_user_missing_fields(self, api_client, server_available):
        """測試註冊時缺少必要欄位"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        invalid_data = {"email": "test@example.com"}  # 缺少 username 和 password
        response = api_client.post("/api/auth/register", json=invalid_data)
        
        if response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert response.status_code == 400
        data = response.json()
        assert "message" in data
    
    def test_register_user_invalid_email(self, api_client, unique_user_data, server_available):
        """測試無效郵箱格式"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        unique_user_data["email"] = "invalid-email"  # 修改為無效郵箱
        response = api_client.post("/api/auth/register", json=unique_user_data)
        
        if response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert response.status_code == 400
        data = response.json()
        assert "message" in data
    
    def test_register_user_username_with_at_symbol(self, api_client, unique_user_data, server_available):
        """測試用戶名包含@符號"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        unique_user_data["username"] = "test@user"  # 修改為包含@的用戶名
        response = api_client.post("/api/auth/register", json=unique_user_data)
        
        if response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert response.status_code == 400
        data = response.json()
        assert "message" in data
    
    def test_register_duplicate_user(self, api_client, unique_user_data):
        """測試重複註冊相同用戶"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 第一次註冊
        first_response = api_client.post("/api/auth/register", json=unique_user_data)
        
        if first_response.status_code in [200, 201]:
            # 第二次註冊相同用戶
            second_response = api_client.post("/api/auth/register", json=unique_user_data)
            assert second_response.status_code == 409
            data = second_response.json()
            assert "message" in data
            
            # Clean up - delete the test account
            self._cleanup_user(api_client, unique_user_data)
    
    def test_login_with_username_success(self, api_client, unique_user_data):
        """測試使用用戶名登入"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 先註冊用戶
        register_response = api_client.post("/api/auth/register", json=unique_user_data)
        
        if register_response.status_code in [200, 201]:
            # 測試登入
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            response = api_client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["message"] == "Login successful"
            
            # Clean up - delete the test account
            self._cleanup_user(api_client, unique_user_data)
    
    def test_login_with_email_success(self, api_client, unique_user_data):
        """測試使用郵箱登入"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 先註冊用戶
        register_response = api_client.post("/api/auth/register", json=unique_user_data)
        
        if register_response.status_code in [200, 201]:
            # 測試用郵箱登入
            login_data = {
                "username": unique_user_data["email"],  # 使用郵箱作為 username
                "password": unique_user_data["password"]
            }
            response = api_client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            
            # Clean up - delete the test account
            self._cleanup_user(api_client, unique_user_data)
    
    def test_login_invalid_credentials(self, api_client, server_available):
        """測試無效登入憑證"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        login_data = {
            "username": "nonexistent_user_12345",
            "password": "wrongpassword"
        }
        response = api_client.post("/api/auth/login", json=login_data)
        
        if response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert response.status_code == 401
        data = response.json()
        assert "message" in data
    
    def test_login_missing_fields(self, api_client, server_available):
        """測試登入時缺少必要欄位"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        login_data = {"username": "testuser"}  # 缺少密碼
        response = api_client.post("/api/auth/login", json=login_data)
        
        if response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert response.status_code == 400
        data = response.json()
        assert "message" in data
    
    def test_get_profile_without_token(self, api_client, server_available):
        """測試未授權訪問個人資料"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        response = api_client.get("/api/profile/")
        
        if response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert response.status_code == 401
    
    def test_delete_account_success(self, api_client, unique_user_data):
        """測試刪除帳號 - 需要密碼確認"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 先註冊用戶
        register_response = api_client.post("/api/auth/register", json=unique_user_data)
        
        if register_response.status_code in [200, 201]:
            # 登入獲取 token
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            login_response = api_client.post("/api/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # 刪除帳號 - 提供密碼確認
                delete_data = {"password": unique_user_data["password"]}
                delete_response = api_client.delete("/api/profile/delete", json=delete_data, headers=headers)
                assert delete_response.status_code == 200
                data = delete_response.json()
                assert data["message"] == "Account and all associated data deleted successfully"
                
                # 嘗試再次登入應該失敗
                login_again = api_client.post("/api/auth/login", json=login_data)
                assert login_again.status_code == 401

    def test_delete_account_without_password(self, api_client, unique_user_data, server_available):
        """測試刪除帳號 - 缺少密碼確認"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 先註冊用戶
        register_response = api_client.post("/api/auth/register", json=unique_user_data)

        if register_response.status_code in [200, 201]:
            # 登入獲取 token
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            login_response = api_client.post("/api/auth/login", json=login_data)

            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}

                # 嘗試刪除帳號但不提供密碼 - 發送空的 JSON 對象
                delete_response = api_client.delete("/api/profile/delete", json={}, headers=headers)
                
                if delete_response.status_code == 503:
                    pytest.skip("服務器不可用")
                
                assert delete_response.status_code == 400
                data = delete_response.json()
                assert "Password confirmation required" in data.get("message", "")
                
                # Clean up - delete the test account
                self._cleanup_user(api_client, unique_user_data)

    def test_delete_account_with_empty_password(self, api_client, unique_user_data, server_available):
        """測試刪除帳號 - 提供空密碼"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 先註冊用戶
        register_response = api_client.post("/api/auth/register", json=unique_user_data)

        if register_response.status_code in [200, 201]:
            # 登入獲取 token
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            login_response = api_client.post("/api/auth/login", json=login_data)

            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}

                # 嘗試刪除帳號但提供空密碼
                delete_data = {"password": ""}
                delete_response = api_client.delete("/api/profile/delete", json=delete_data, headers=headers)
                
                if delete_response.status_code == 503:
                    pytest.skip("服務器不可用")
                
                assert delete_response.status_code == 400
                data = delete_response.json()
                assert "Password confirmation required" in data.get("message", "")
                
                # Clean up - delete the test account
                self._cleanup_user(api_client, unique_user_data)

    def test_delete_account_with_null_password(self, api_client, unique_user_data, server_available):
        """測試刪除帳號 - 提供 null 密碼"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 先註冊用戶
        register_response = api_client.post("/api/auth/register", json=unique_user_data)

        if register_response.status_code in [200, 201]:
            # 登入獲取 token
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            login_response = api_client.post("/api/auth/login", json=login_data)

            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}

                # 嘗試刪除帳號但提供 null 密碼
                delete_data = {"password": None}
                delete_response = api_client.delete("/api/profile/delete", json=delete_data, headers=headers)
                
                if delete_response.status_code == 503:
                    pytest.skip("服務器不可用")
                
                assert delete_response.status_code == 400
                data = delete_response.json()
                assert "Password confirmation required" in data.get("message", "")
                
                # Clean up - delete the test account
                self._cleanup_user(api_client, unique_user_data)

    def test_delete_account_without_json_content_type(self, api_client, unique_user_data, server_available):
        """測試刪除帳號 - 不使用 JSON Content-Type（應該改為測試非 JSON 請求）"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 先註冊用戶
        register_response = api_client.post("/api/auth/register", json=unique_user_data)

        if register_response.status_code in [200, 201]:
            # 登入獲取 token
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            login_response = api_client.post("/api/auth/login", json=login_data)

            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                
                # 測試發送表單數據而不是 JSON
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                delete_response = api_client.delete("/api/profile/delete", data="password=test", headers=headers)
                
                if delete_response.status_code == 503:
                    pytest.skip("服務器不可用")
                
                assert delete_response.status_code == 400
                data = delete_response.json()
                assert "Password confirmation required" in data.get("message", "")
                
                # Clean up - delete the test account
                self._cleanup_user(api_client, unique_user_data)

    def test_delete_account_with_invalid_token(self, api_client, server_available):
        """測試刪除帳號 - 無效的 token"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 使用無效的 token
        headers = {"Authorization": "Bearer invalid_token_12345"}
        delete_data = {"password": "testpassword123"}
        
        delete_response = api_client.delete("/api/profile/delete", json=delete_data, headers=headers)
        
        if delete_response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert delete_response.status_code == 401
        data = delete_response.json()
        assert "message" in data  # JWT 相關的錯誤訊息

    def test_delete_account_with_expired_token(self, api_client, server_available):
        """測試刪除帳號 - 過期的 token（模擬）"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 使用格式正確但過期的 token
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYwMDAwMDAwMCwianRpIjoiZXhwaXJlZC10b2tlbiIsInR5cGUiOiJhY2Nlc3MiLCJzdWIiOiJ0ZXN0LXVzZXIiLCJuYmYiOjE2MDAwMDAwMDAsImV4cCI6MTYwMDAwMDAwMX0.invalid"
        headers = {"Authorization": f"Bearer {expired_token}"}
        delete_data = {"password": "testpassword123"}
        
        delete_response = api_client.delete("/api/profile/delete", json=delete_data, headers=headers)
        
        if delete_response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert delete_response.status_code == 401  # JWT 驗證失敗

    def test_delete_account_with_malformed_authorization_header(self, api_client, server_available):
        """測試刪除帳號 - 格式錯誤的 Authorization header"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 測試各種錯誤的 Authorization header 格式
        malformed_headers = [
            {"Authorization": "invalid_format"},
            {"Authorization": "Bearer"},  # 缺少 token
            {"Authorization": "Basic token123"},  # 錯誤的認證類型
            {"Authorization": "Bearer "},  # 空的 token
        ]
        
        delete_data = {"password": "testpassword123"}
        
        for headers in malformed_headers:
            delete_response = api_client.delete("/api/profile/delete", json=delete_data, headers=headers)
            
            if delete_response.status_code == 503:
                pytest.skip("服務器不可用")
            
            assert delete_response.status_code == 401, f"Failed for headers: {headers}"

    def test_delete_account_comprehensive_auth_flow(self, api_client, unique_user_data, server_available):
        """測試刪除帳號 - 完整的認證流程測試"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        # 1. 先測試沒有 token 的情況
        delete_data = {"password": "testpassword123"}
        delete_response = api_client.delete("/api/profile/delete", json=delete_data)
        
        if delete_response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert delete_response.status_code == 401
        
        # 2. 註冊用戶
        register_response = api_client.post("/api/auth/register", json=unique_user_data)
        
        if register_response.status_code in [200, 201]:
            # 3. 登入獲取有效 token
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            login_response = api_client.post("/api/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # 4. 測試有 token 但沒有密碼
                delete_response = api_client.delete("/api/profile/delete", json={}, headers=headers)
                assert delete_response.status_code == 400
                data = delete_response.json()
                assert "Password confirmation required" in data.get("message", "")
                
                # 5. 測試有 token 但密碼錯誤
                wrong_password_data = {"password": "wrongpassword123"}
                delete_response = api_client.delete("/api/profile/delete", json=wrong_password_data, headers=headers)
                assert delete_response.status_code == 401
                data = delete_response.json()
                assert "Invalid password" in data.get("message", "")
                
                # 6. 測試正確的 token 和密碼（實際刪除）
                correct_password_data = {"password": unique_user_data["password"]}
                delete_response = api_client.delete("/api/profile/delete", json=correct_password_data, headers=headers)
                assert delete_response.status_code == 200
                data = delete_response.json()
                assert "Account and all associated data deleted successfully" in data.get("message", "")
                
                # 7. 驗證帳號已被刪除 - 嘗試再次登入應該失敗
                login_again = api_client.post("/api/auth/login", json=login_data)
                assert login_again.status_code == 401

    def test_delete_account_without_token(self, api_client, server_available):
        """測試未授權刪除帳號"""
        if not self.is_server_available():
            pytest.skip("服務器不可用，跳過測試")
        
        delete_data = {"password": "testpassword123"}
        response = api_client.delete("/api/profile/delete", json=delete_data)
        
        if response.status_code == 503:
            pytest.skip("服務器不可用")
        
        assert response.status_code == 401
    
    def _cleanup_user(self, api_client, user_data):
        """清理測試用戶"""
        try:
            # 嘗試登入獲取 token
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            login_response = api_client.post("/api/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # 刪除帳號
                delete_data = {"password": user_data["password"]}
                api_client.delete("/api/profile/delete", json=delete_data, headers=headers)
        except:
            # 如果清理失敗，忽略錯誤
            pass
