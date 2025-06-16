import pytest
import json

from conftest import unique_user_data

@pytest.mark.api
class TestUsersAPI:
    """用戶 API 測試"""
    
    def test_register_user_success(self, api_client, unique_user_data):
        """測試用戶註冊"""
        response = api_client.post("/register", json=unique_user_data)
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "user_id" in data
        assert data["message"] == "User registered successfully"
    
    def test_register_user_missing_fields(self, api_client):
        """測試註冊時缺少必要欄位"""
        invalid_data = {"email": "test@example.com"}  # 缺少 username 和 password
        response = api_client.post("/register", json=invalid_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_register_user_invalid_email(self, api_client, unique_user_data):
        """測試無效郵箱格式"""
        unique_user_data["email"] = "invalid-email"  # 修改為無效郵箱
        response = api_client.post("/register", json=unique_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_register_user_username_with_at_symbol(self, api_client, unique_user_data):
        """測試用戶名包含@符號"""
        unique_user_data["username"] = "test@user"  # 修改為包含@的用戶名
        response = api_client.post("/register", json=unique_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_register_duplicate_user(self, api_client, unique_user_data):
        """測試重複註冊相同用戶"""
        # 第一次註冊
        first_response = api_client.post("/register", json=unique_user_data)
        
        if first_response.status_code in [200, 201]:
            # 第二次註冊相同用戶
            second_response = api_client.post("/register", json=unique_user_data)
            assert second_response.status_code == 409
            data = second_response.json()
            assert "error" in data
    
    def test_login_with_username_success(self, api_client, unique_user_data):
        """測試使用用戶名登入"""
        # 先註冊用戶
        register_response = api_client.post("/register", json=unique_user_data)
        
        if register_response.status_code in [200, 201]:
            # 測試登入
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            response = api_client.post("/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["message"] == "Login successful"
    
    def test_login_with_email_success(self, api_client, unique_user_data):
        """測試使用郵箱登入"""
        # 先註冊用戶
        register_response = api_client.post("/register", json=unique_user_data)
        
        if register_response.status_code in [200, 201]:
            # 測試用郵箱登入
            login_data = {
                "username": unique_user_data["email"],  # 使用郵箱作為 username
                "password": unique_user_data["password"]
            }
            response = api_client.post("/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
    
    def test_login_invalid_credentials(self, api_client):
        """測試無效登入憑證"""
        login_data = {
            "username": "nonexistent_user_12345",
            "password": "wrongpassword"
        }
        response = api_client.post("/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
    
    def test_login_missing_fields(self, api_client):
        """測試登入時缺少必要欄位"""
        login_data = {"username": "testuser"}  # 缺少密碼
        response = api_client.post("/login", json=login_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_get_profile_without_token(self, api_client):
        """測試未授權訪問個人資料"""
        response = api_client.get("/api/profile")
        assert response.status_code == 401
    
    def test_delete_account_success(self, api_client, unique_user_data):
        """測試刪除帳號 - 需要密碼確認"""
        # 先註冊用戶
        register_response = api_client.post("/register", json=unique_user_data)
        
        if register_response.status_code in [200, 201]:
            # 登入獲取 token
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            login_response = api_client.post("/login", json=login_data)
            
            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # 刪除帳號 - 提供密碼確認
                delete_data = {"password": unique_user_data["password"]}
                delete_response = api_client.delete("/delete_account", json=delete_data, headers=headers)
                assert delete_response.status_code == 200
                data = delete_response.json()
                assert data["message"] == "Account and all associated data deleted successfully"
                
                # 嘗試再次登入應該失敗
                login_again = api_client.post("/login", json=login_data)
                assert login_again.status_code == 401

    def test_delete_account_without_password(self, api_client, unique_user_data):
        """測試刪除帳號 - 缺少密碼確認"""
        # 先註冊用戶
        register_response = api_client.post("/register", json=unique_user_data)
        
        if register_response.status_code in [200, 201]:
            # 登入獲取 token
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            login_response = api_client.post("/login", json=login_data)
            
            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # 嘗試刪除帳號但不提供密碼
                delete_response = api_client.delete("/delete_account", headers=headers)
                assert delete_response.status_code == 400
                data = delete_response.json()
                assert "Password confirmation required" in data["error"]

    def test_delete_account_wrong_password(self, api_client, unique_user_data):
        """測試刪除帳號 - 錯誤密碼"""
        # 先註冊用戶
        register_response = api_client.post("/register", json=unique_user_data)
        
        if register_response.status_code in [200, 201]:
            # 登入獲取 token
            login_data = {
                "username": unique_user_data["username"],
                "password": unique_user_data["password"]
            }
            login_response = api_client.post("/login", json=login_data)
            
            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # 嘗試刪除帳號但提供錯誤密碼
                delete_data = {"password": "wrongpassword123"}
                delete_response = api_client.delete("/delete_account", json=delete_data, headers=headers)
                assert delete_response.status_code == 401
                data = delete_response.json()
                assert "Invalid password" in data["error"]

    def test_delete_account_without_token(self, api_client):
        """測試未授權刪除帳號"""
        response = api_client.delete("/delete_account")
        assert response.status_code == 401
    
    def test_deactivate_account_without_token(self, api_client):
        """測試未授權停用帳號"""
        response = api_client.put("/deactivate_account")
        assert response.status_code == 401
        login_data = {
            "username": unique_user_data["username"],
            "password": unique_user_data["password"]
        }
        login_response = api_client.post("/login", json=login_data)
        
        if login_response.status_code == 200:
            access_token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # 停用帳號
            deactivate_response = api_client.put("/deactivate_account", headers=headers)
            assert deactivate_response.status_code == 200
            data = deactivate_response.json()
            assert data["message"] == "Account deactivated successfully"
            
            # 嘗試再次登入應該失敗（帳號已停用）
            login_again = api_client.post("/login", json=login_data)
            assert login_again.status_code == 403

    def test_delete_account_without_token(self, api_client):
        """測試未授權刪除帳號"""
        response = api_client.delete("/delete_account")
        assert response.status_code == 401
    
    def test_deactivate_account_without_token(self, api_client):
        """測試未授權停用帳號"""
        response = api_client.put("/deactivate_account")
        assert response.status_code == 401
