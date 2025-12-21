"""认证API测试"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_user():
    """测试用户注册"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    assert "username" in response.json()


def test_login_user():
    """测试用户登录"""
    # 先注册
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "testpass123"
        }
    )
    
    # 登录
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser2",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_current_user():
    """测试获取当前用户信息"""
    # 注册并登录
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser3",
            "email": "test3@example.com",
            "password": "testpass123"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser3",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # 获取用户信息
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser3"

